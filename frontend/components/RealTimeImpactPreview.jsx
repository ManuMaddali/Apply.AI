/**
 * RealTimeImpactPreview Component
 * Implements live ATS score updates, transformation analytics, and comparison tools
 * Handles real-time impact visualization with animated score progression
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  BarChart3,
  Target,
  Award,
  Zap,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  Download,
  Eye,
  FileText,
  Star,
  Brain,
  Lightbulb,
  Clock,
  Users,
  Crown,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Info,
  Plus,
  Minus
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, hoverLift, scaleIn } from '../lib/motion';

/**
 * LiveATSScoreUpdates Component
 * Subtask 7.1: Create animated score progression with real-time updates
 */
function LiveATSScoreUpdates({
  currentScore,
  targetScore,
  appliedChanges = [],
  onScoreUpdate,
  isAnimating = false,
  className = ''
}) {
  const [displayScore, setDisplayScore] = useState(currentScore);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [animationProgress, setAnimationProgress] = useState(0);

  // Mock applied changes tracking
  const mockAppliedChanges = useMemo(() => appliedChanges.length > 0 ? appliedChanges : [
    {
      id: 'skills-section',
      title: 'Added Skills Section',
      impact: 15,
      status: 'applied',
      timestamp: new Date(Date.now() - 30000),
      keywords: ['React', 'Node.js', 'Python', 'AWS'],
      category: 'structure'
    },
    {
      id: 'summary-enhancement',
      title: 'Enhanced Professional Summary',
      impact: 8,
      status: 'applied',
      timestamp: new Date(Date.now() - 20000),
      keywords: ['Senior', 'Leadership', 'Scalable'],
      category: 'content'
    },
    {
      id: 'experience-bullets',
      title: 'Improved 3 Experience Bullets',
      impact: 12,
      status: 'applied',
      timestamp: new Date(Date.now() - 10000),
      keywords: ['Performance', 'Optimization', 'Team'],
      category: 'quantification'
    },
    {
      id: 'education-optimization',
      title: 'Education Section Optimization',
      impact: 4,
      status: 'pending',
      timestamp: new Date(),
      keywords: ['Relevant Coursework', 'Projects'],
      category: 'formatting'
    }
  ], [appliedChanges]);

  // Animate score progression
  useEffect(() => {
    if (isAnimating && targetScore !== displayScore) {
      const duration = 2000; // 2 seconds
      const startScore = displayScore;
      const scoreDiff = targetScore - startScore;
      const startTime = Date.now();

      const animateScore = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const newScore = Math.round(startScore + (scoreDiff * easeOutCubic));
        
        setDisplayScore(newScore);
        setAnimationProgress(progress);
        
        if (progress < 1) {
          requestAnimationFrame(animateScore);
        } else {
          onScoreUpdate?.(targetScore);
        }
      };

      requestAnimationFrame(animateScore);
    }
  }, [targetScore, displayScore, isAnimating, onScoreUpdate]);

  // Track score history
  useEffect(() => {
    if (displayScore !== currentScore) {
      setScoreHistory(prev => [...prev, {
        score: displayScore,
        timestamp: new Date(),
        change: displayScore - (prev[prev.length - 1]?.score || currentScore)
      }].slice(-10)); // Keep last 10 changes
    }
  }, [displayScore, currentScore]);

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreGradient = (score) => {
    if (score >= 90) return 'from-green-500 to-emerald-600';
    if (score >= 70) return 'from-blue-500 to-indigo-600';
    if (score >= 50) return 'from-amber-500 to-orange-600';
    return 'from-red-500 to-rose-600';
  };

  const getImpactColor = (impact) => {
    if (impact >= 15) return 'text-green-600 bg-green-50 border-green-200';
    if (impact >= 10) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (impact >= 5) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      structure: Target,
      content: FileText,
      quantification: BarChart3,
      formatting: Sparkles
    };
    return icons[category] || CheckCircle;
  };

  const totalAppliedImpact = mockAppliedChanges
    .filter(change => change.status === 'applied')
    .reduce((sum, change) => sum + change.impact, 0);

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
                  <TrendingUp className="w-5 h-5" />
                  Live ATS Score
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Real-time updates as enhancements are applied
                </EnhancedCardDescription>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowBreakdown(!showBreakdown)}
                className="text-blue-600 border-blue-300"
              >
                <Info className="w-4 h-4 mr-2" />
                {showBreakdown ? 'Hide' : 'Show'} Breakdown
              </Button>
            </div>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Current Score Circle */}
              <div className="text-center">
                <div className="relative w-32 h-32 mx-auto mb-4">
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
                      stroke="url(#scoreGradient)"
                      strokeWidth="8"
                      fill="none"
                      strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 40}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                      animate={{ 
                        strokeDashoffset: 2 * Math.PI * 40 * (1 - displayScore / 100) 
                      }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                    />
                    <defs>
                      <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" className={`stop-color-${getScoreGradient(displayScore).split('-')[1]}-500`} />
                        <stop offset="100%" className={`stop-color-${getScoreGradient(displayScore).split('-')[3]}-600`} />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <motion.div
                        key={displayScore}
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className={`text-3xl font-bold ${getScoreColor(displayScore)}`}
                      >
                        {displayScore}
                      </motion.div>
                      <div className="text-xs text-gray-500">/ 100</div>
                    </div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Current Score</h3>
                <p className="text-sm text-gray-600">ATS Compatibility</p>
              </div>

              {/* Target Score */}
              <div className="text-center">
                <div className="relative w-32 h-32 mx-auto mb-4">
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
                      className="text-green-500"
                      strokeDasharray={`${2 * Math.PI * 40}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                      animate={{ 
                        strokeDashoffset: 2 * Math.PI * 40 * (1 - targetScore / 100) 
                      }}
                      transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        {targetScore}
                      </div>
                      <div className="text-xs text-gray-500">/ 100</div>
                    </div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Target Score</h3>
                <p className="text-sm text-gray-600">With All Changes</p>
              </div>

              {/* Improvement */}
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100 rounded-full">
                  <div className="text-center">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.6, delay: 0.8 }}
                      className="text-3xl font-bold text-purple-600"
                    >
                      +{targetScore - currentScore}
                    </motion.div>
                    <div className="text-xs text-purple-700">points</div>
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900">Total Improvement</h3>
                <p className="text-sm text-gray-600">Potential Gain</p>
              </div>
            </div>

            {/* Progress Indicator */}
            {isAnimating && (
              <div className="mt-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Updating Score</span>
                  <span className="text-sm text-gray-600">
                    {Math.round(animationProgress * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${animationProgress * 100}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            )}

            {/* Score Breakdown */}
            <AnimatePresence>
              {showBreakdown && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden mt-6 pt-6 border-t border-gray-200"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Score Components</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Content Quality</span>
                          <span className="font-medium">{Math.round(displayScore * 0.4)}/40</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Keyword Optimization</span>
                          <span className="font-medium">{Math.round(displayScore * 0.3)}/30</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Structure & Format</span>
                          <span className="font-medium">{Math.round(displayScore * 0.2)}/20</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Job Relevance</span>
                          <span className="font-medium">{Math.round(displayScore * 0.1)}/10</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Recent Changes</h4>
                      <div className="space-y-2">
                        {scoreHistory.slice(-3).map((entry, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">
                              {entry.timestamp.toLocaleTimeString()}
                            </span>
                            <span className={`font-medium ${
                              entry.change > 0 ? 'text-green-600' : 
                              entry.change < 0 ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {entry.change > 0 ? '+' : ''}{entry.change} pts
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Applied Changes Tracking */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Applied Changes
              <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getImpactColor(totalAppliedImpact)}`}>
                +{totalAppliedImpact} points
              </div>
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Track impact of each enhancement as it's applied
            </EnhancedCardDescription>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="space-y-4">
              {mockAppliedChanges.map((change, index) => {
                const Icon = getCategoryIcon(change.category);
                
                return (
                  <motion.div
                    key={change.id}
                    variants={staggerItem}
                    className={`p-4 rounded-lg border transition-all duration-200 ${
                      change.status === 'applied' 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-full ${
                          change.status === 'applied' 
                            ? 'bg-green-100 text-green-600' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-gray-900">{change.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {change.status === 'applied' 
                              ? `Applied ${Math.round((Date.now() - change.timestamp) / 1000)}s ago`
                              : 'Ready to apply'
                            }
                          </p>
                          
                          {/* Keywords Added */}
                          {change.keywords && change.keywords.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs text-gray-500 mb-1">Keywords Added:</div>
                              <div className="flex flex-wrap gap-1">
                                {change.keywords.map((keyword, idx) => (
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
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getImpactColor(change.impact)}`}>
                          +{change.impact} pts
                        </div>
                        
                        {change.status === 'applied' ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <Clock className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>
    </motion.div>
  );
}

export { LiveATSScoreUpdates };
export default LiveATSScoreUpdates;

/**
 * KeywordAnalysisVisualization Component
 * Part of subtask 7.1: Add keyword analysis visualization with categories
 */
function KeywordAnalysisVisualization({
  keywordData,
  showCategories = true,
  onKeywordClick,
  className = ''
}) {
  const [expandedCategories, setExpandedCategories] = useState(['technical']);
  const [sortBy, setSortBy] = useState('relevance'); // relevance, frequency, alphabetical

  // Mock keyword data if not provided
  const mockKeywordData = useMemo(() => keywordData || {
    added: [
      { term: 'React', category: 'technical', relevance: 95, frequency: 8, impact: 'high' },
      { term: 'Node.js', category: 'technical', relevance: 90, frequency: 6, impact: 'high' },
      { term: 'Leadership', category: 'soft_skills', relevance: 85, frequency: 4, impact: 'medium' },
      { term: 'Scalable', category: 'impact', relevance: 88, frequency: 5, impact: 'high' },
      { term: 'Performance', category: 'impact', relevance: 82, frequency: 7, impact: 'medium' },
      { term: 'AWS', category: 'technical', relevance: 92, frequency: 3, impact: 'high' },
      { term: 'Agile', category: 'process', relevance: 75, frequency: 4, impact: 'medium' },
      { term: 'Team Collaboration', category: 'soft_skills', relevance: 78, frequency: 3, impact: 'medium' }
    ],
    removed: [
      { term: 'Basic', category: 'impact', relevance: 20, frequency: 2, impact: 'negative' },
      { term: 'Simple', category: 'impact', relevance: 15, frequency: 1, impact: 'negative' }
    ],
    categories: [
      { name: 'technical', label: 'Technical Skills', count: 3, color: 'blue' },
      { name: 'soft_skills', label: 'Soft Skills', count: 2, color: 'green' },
      { name: 'impact', label: 'Impact Words', count: 2, color: 'purple' },
      { name: 'process', label: 'Process & Methods', count: 1, color: 'amber' }
    ]
  }, [keywordData]);

  const toggleCategory = (categoryName) => {
    setExpandedCategories(prev => 
      prev.includes(categoryName)
        ? prev.filter(name => name !== categoryName)
        : [...prev, categoryName]
    );
  };

  const sortKeywords = (keywords) => {
    return [...keywords].sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          return b.relevance - a.relevance;
        case 'frequency':
          return b.frequency - a.frequency;
        case 'alphabetical':
          return a.term.localeCompare(b.term);
        default:
          return 0;
      }
    });
  };

  const getKeywordColor = (category, impact) => {
    if (impact === 'negative') return 'bg-red-100 text-red-700 border-red-200';
    
    const colors = {
      technical: 'bg-blue-100 text-blue-700 border-blue-200',
      soft_skills: 'bg-green-100 text-green-700 border-green-200',
      impact: 'bg-purple-100 text-purple-700 border-purple-200',
      process: 'bg-amber-100 text-amber-700 border-amber-200'
    };
    return colors[category] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getImpactIcon = (impact) => {
    switch (impact) {
      case 'high':
        return <TrendingUp className="w-3 h-3 text-green-600" />;
      case 'medium':
        return <ArrowRight className="w-3 h-3 text-blue-600" />;
      case 'negative':
        return <Minus className="w-3 h-3 text-red-600" />;
      default:
        return <Plus className="w-3 h-3 text-gray-600" />;
    }
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      <EnhancedCard>
        <EnhancedCardHeader>
          <div className="flex items-center justify-between">
            <div>
              <EnhancedCardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Keyword Analysis
                <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                  <Plus className="w-3 h-3" />
                  {mockKeywordData.added.length} added
                </div>
                {mockKeywordData.removed.length > 0 && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded text-sm font-medium">
                    <Minus className="w-3 h-3" />
                    {mockKeywordData.removed.length} removed
                  </div>
                )}
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                Keywords optimized for ATS compatibility and job relevance
              </EnhancedCardDescription>
            </div>
            
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="relevance">Sort by Relevance</option>
                <option value="frequency">Sort by Frequency</option>
                <option value="alphabetical">Sort Alphabetically</option>
              </select>
            </div>
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent>
          {/* Category Overview */}
          {showCategories && (
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-3">Categories</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {mockKeywordData.categories.map((category) => (
                  <motion.div
                    key={category.name}
                    variants={staggerItem}
                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                      expandedCategories.includes(category.name)
                        ? `bg-${category.color}-50 border-${category.color}-200`
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                    }`}
                    onClick={() => toggleCategory(category.name)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium text-gray-900 text-sm">{category.label}</h5>
                        <p className="text-xs text-gray-600">{category.count} keywords</p>
                      </div>
                      {expandedCategories.includes(category.name) ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Added Keywords */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Plus className="w-4 h-4 text-green-600" />
              Keywords Added ({mockKeywordData.added.length})
            </h4>
            
            {showCategories ? (
              // Grouped by category
              <div className="space-y-4">
                {mockKeywordData.categories
                  .filter(cat => expandedCategories.includes(cat.name))
                  .map((category) => {
                    const categoryKeywords = sortKeywords(
                      mockKeywordData.added.filter(kw => kw.category === category.name)
                    );
                    
                    if (categoryKeywords.length === 0) return null;
                    
                    return (
                      <div key={category.name}>
                        <h5 className="text-sm font-medium text-gray-700 mb-2 capitalize">
                          {category.label}
                        </h5>
                        <div className="flex flex-wrap gap-2">
                          {categoryKeywords.map((keyword, index) => (
                            <motion.button
                              key={`${keyword.term}-${index}`}
                              variants={staggerItem}
                              className={`px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-200 hover:scale-105 ${getKeywordColor(keyword.category, keyword.impact)}`}
                              onClick={() => onKeywordClick?.(keyword)}
                            >
                              <div className="flex items-center gap-2">
                                {getImpactIcon(keyword.impact)}
                                <span>{keyword.term}</span>
                                <div className="flex items-center gap-1 text-xs opacity-75">
                                  <span>{keyword.relevance}%</span>
                                  <span>•</span>
                                  <span>{keyword.frequency}x</span>
                                </div>
                              </div>
                            </motion.button>
                          ))}
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              // All keywords together
              <div className="flex flex-wrap gap-2">
                {sortKeywords(mockKeywordData.added).map((keyword, index) => (
                  <motion.button
                    key={`${keyword.term}-${index}`}
                    variants={staggerItem}
                    className={`px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-200 hover:scale-105 ${getKeywordColor(keyword.category, keyword.impact)}`}
                    onClick={() => onKeywordClick?.(keyword)}
                  >
                    <div className="flex items-center gap-2">
                      {getImpactIcon(keyword.impact)}
                      <span>{keyword.term}</span>
                      <div className="flex items-center gap-1 text-xs opacity-75">
                        <span>{keyword.relevance}%</span>
                        <span>•</span>
                        <span>{keyword.frequency}x</span>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            )}
          </div>

          {/* Removed Keywords */}
          {mockKeywordData.removed.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Minus className="w-4 h-4 text-red-600" />
                Keywords Removed ({mockKeywordData.removed.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {mockKeywordData.removed.map((keyword, index) => (
                  <motion.div
                    key={`removed-${keyword.term}-${index}`}
                    variants={staggerItem}
                    className="px-3 py-2 rounded-lg border text-sm font-medium bg-red-50 text-red-700 border-red-200 opacity-75"
                  >
                    <div className="flex items-center gap-2">
                      <Minus className="w-3 h-3" />
                      <span className="line-through">{keyword.term}</span>
                      <div className="text-xs opacity-75">
                        {keyword.relevance}%
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Keyword Statistics */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(mockKeywordData.added.reduce((sum, kw) => sum + kw.relevance, 0) / mockKeywordData.added.length)}%
                </div>
                <div className="text-sm text-gray-600">Avg. Relevance</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {mockKeywordData.added.reduce((sum, kw) => sum + kw.frequency, 0)}
                </div>
                <div className="text-sm text-gray-600">Total Mentions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {mockKeywordData.added.filter(kw => kw.impact === 'high').length}
                </div>
                <div className="text-sm text-gray-600">High Impact</div>
              </div>
            </div>
          </div>
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * JobMatchImprovementMetrics Component
 * Part of subtask 7.1: Implement job match improvement metrics
 */
function JobMatchImprovementMetrics({
  beforeMetrics,
  afterMetrics,
  showDetails = false,
  className = ''
}) {
  const [expandedMetrics, setExpandedMetrics] = useState(false);

  // Mock metrics data if not provided
  const mockBeforeMetrics = beforeMetrics || {
    overallMatch: 52,
    skillsMatch: 6,
    totalSkills: 12,
    experienceRelevance: 68,
    keywordDensity: 2.3,
    industryAlignment: 75,
    missingKeywords: ['React', 'Leadership', 'Agile', 'AWS', 'Python', 'Kubernetes']
  };

  const mockAfterMetrics = afterMetrics || {
    overallMatch: 89,
    skillsMatch: 11,
    totalSkills: 12,
    experienceRelevance: 92,
    keywordDensity: 4.8,
    industryAlignment: 95,
    missingKeywords: ['Kubernetes']
  };

  const improvements = {
    overallMatch: mockAfterMetrics.overallMatch - mockBeforeMetrics.overallMatch,
    skillsMatch: mockAfterMetrics.skillsMatch - mockBeforeMetrics.skillsMatch,
    experienceRelevance: mockAfterMetrics.experienceRelevance - mockBeforeMetrics.experienceRelevance,
    keywordDensity: mockAfterMetrics.keywordDensity - mockBeforeMetrics.keywordDensity,
    industryAlignment: mockAfterMetrics.industryAlignment - mockBeforeMetrics.industryAlignment,
    keywordsAdded: mockBeforeMetrics.missingKeywords.length - mockAfterMetrics.missingKeywords.length
  };

  const getImprovementColor = (value) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getImprovementIcon = (value) => {
    if (value > 0) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (value < 0) return <TrendingUp className="w-4 h-4 text-red-600 rotate-180" />;
    return <ArrowRight className="w-4 h-4 text-gray-600" />;
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      <EnhancedCard>
        <EnhancedCardHeader>
          <div className="flex items-center justify-between">
            <div>
              <EnhancedCardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Job Match Improvement
                <div className={`px-3 py-1 rounded-full text-sm font-medium border ${
                  improvements.overallMatch > 0 ? 'text-green-600 bg-green-50 border-green-200' : 'text-gray-600 bg-gray-50 border-gray-200'
                }`}>
                  {improvements.overallMatch > 0 ? '+' : ''}{improvements.overallMatch}% match
                </div>
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                How your resume now aligns with job requirements
              </EnhancedCardDescription>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setExpandedMetrics(!expandedMetrics)}
              className="text-blue-600 border-blue-300"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              {expandedMetrics ? 'Hide' : 'Show'} Details
            </Button>
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent>
          {/* Main Improvement Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Overall Match */}
            <div className="text-center">
              <div className="relative w-24 h-24 mx-auto mb-3">
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
                    className="text-green-500"
                    strokeDasharray={`${2 * Math.PI * 35}`}
                    initial={{ strokeDashoffset: 2 * Math.PI * 35 }}
                    animate={{ 
                      strokeDashoffset: 2 * Math.PI * 35 * (1 - mockAfterMetrics.overallMatch / 100) 
                    }}
                    transition={{ duration: 1.5, delay: 0.3 }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">
                      {mockAfterMetrics.overallMatch}%
                    </div>
                  </div>
                </div>
              </div>
              <h4 className="font-medium text-gray-900">Overall Match</h4>
              <div className="flex items-center justify-center gap-1 mt-1">
                {getImprovementIcon(improvements.overallMatch)}
                <span className={`text-sm font-medium ${getImprovementColor(improvements.overallMatch)}`}>
                  {improvements.overallMatch > 0 ? '+' : ''}{improvements.overallMatch}%
                </span>
              </div>
            </div>

            {/* Skills Match */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-3 flex items-center justify-center bg-blue-100 rounded-full">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">
                    {mockAfterMetrics.skillsMatch}/{mockAfterMetrics.totalSkills}
                  </div>
                  <div className="text-xs text-blue-700">skills</div>
                </div>
              </div>
              <h4 className="font-medium text-gray-900">Skills Matched</h4>
              <div className="flex items-center justify-center gap-1 mt-1">
                {getImprovementIcon(improvements.skillsMatch)}
                <span className={`text-sm font-medium ${getImprovementColor(improvements.skillsMatch)}`}>
                  +{improvements.skillsMatch} skills
                </span>
              </div>
            </div>

            {/* Experience Relevance */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-3 flex items-center justify-center bg-purple-100 rounded-full">
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600">
                    {mockAfterMetrics.experienceRelevance}%
                  </div>
                  <div className="text-xs text-purple-700">relevant</div>
                </div>
              </div>
              <h4 className="font-medium text-gray-900">Experience Match</h4>
              <div className="flex items-center justify-center gap-1 mt-1">
                {getImprovementIcon(improvements.experienceRelevance)}
                <span className={`text-sm font-medium ${getImprovementColor(improvements.experienceRelevance)}`}>
                  {improvements.experienceRelevance > 0 ? '+' : ''}{improvements.experienceRelevance}%
                </span>
              </div>
            </div>
          </div>

          {/* Before/After Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                Before Enhancement
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Overall Match</span>
                  <span className="font-medium text-red-600">{mockBeforeMetrics.overallMatch}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Skills Matched</span>
                  <span className="font-medium text-red-600">
                    {mockBeforeMetrics.skillsMatch}/{mockBeforeMetrics.totalSkills}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Missing Keywords</span>
                  <span className="font-medium text-red-600">{mockBeforeMetrics.missingKeywords.length}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                After Enhancement
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Overall Match</span>
                  <span className="font-medium text-green-600">{mockAfterMetrics.overallMatch}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Skills Matched</span>
                  <span className="font-medium text-green-600">
                    {mockAfterMetrics.skillsMatch}/{mockAfterMetrics.totalSkills}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Missing Keywords</span>
                  <span className="font-medium text-green-600">{mockAfterMetrics.missingKeywords.length}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Metrics */}
          <AnimatePresence>
            {expandedMetrics && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden mt-6 pt-6 border-t border-gray-200"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-gray-900 mb-3">Improvement Breakdown</h5>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <span className="text-sm text-gray-700">Keyword Density</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">{mockBeforeMetrics.keywordDensity}%</span>
                          <ArrowRight className="w-3 h-3 text-gray-400" />
                          <span className="text-sm font-medium text-green-600">{mockAfterMetrics.keywordDensity}%</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <span className="text-sm text-gray-700">Industry Alignment</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">{mockBeforeMetrics.industryAlignment}%</span>
                          <ArrowRight className="w-3 h-3 text-gray-400" />
                          <span className="text-sm font-medium text-blue-600">{mockAfterMetrics.industryAlignment}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h5 className="font-medium text-gray-900 mb-3">Remaining Gaps</h5>
                    {mockAfterMetrics.missingKeywords.length > 0 ? (
                      <div className="space-y-2">
                        <p className="text-sm text-gray-600">Still missing these keywords:</p>
                        <div className="flex flex-wrap gap-2">
                          {mockAfterMetrics.missingKeywords.map((keyword, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="text-sm text-green-700">All required keywords matched!</span>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
}/**

 * TransformationAnalytics Component
 * Subtask 7.2: Show estimated interview rate improvement calculations and detailed analytics
 */
function TransformationAnalytics({
  transformationData,
  isProUser = false,
  onUpgradeClick,
  className = ''
}) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('30days');
  const [showDetailedBreakdown, setShowDetailedBreakdown] = useState(false);
  const [exportFormat, setExportFormat] = useState('pdf');

  // Mock transformation data if not provided
  const mockTransformationData = useMemo(() => transformationData || {
    interviewRateImprovement: {
      before: 12, // 12% interview rate
      after: 28,  // 28% interview rate
      improvement: 16, // +16 percentage points
      confidence: 'high',
      basedOnApplications: 150
    },
    keywordAnalysis: {
      totalAdded: 18,
      totalRemoved: 3,
      relevanceScore: 92,
      categories: {
        technical: { added: 8, relevance: 95 },
        soft_skills: { added: 4, relevance: 88 },
        impact: { added: 6, relevance: 90 }
      }
    },
    contentEnhancement: {
      sectionsImproved: 4,
      bulletsEnhanced: 12,
      metricsAdded: 8,
      actionVerbsStrengthened: 15,
      wordCountChange: 127, // +127 words
      readabilityScore: 85
    },
    atsCompatibility: {
      beforeScore: 67,
      afterScore: 94,
      improvement: 27,
      passRate: 96, // % of ATS systems that would pass this resume
      industryBenchmark: 78
    },
    estimatedImpact: {
      applicationSuccess: {
        before: 8.5, // % of applications leading to interviews
        after: 19.2,
        timeframe: '30 days'
      },
      salaryPotential: {
        increase: 12000, // estimated salary increase
        confidence: 'medium',
        basedOn: 'market_analysis'
      },
      timeToHire: {
        reduction: 18, // days reduced
        confidence: 'high'
      }
    }
  }, [transformationData]);

  const handleExportReport = () => {
    if (!isProUser) {
      onUpgradeClick?.();
      return;
    }
    
    // Mock export functionality
    console.log(`Exporting analytics report as ${exportFormat}`);
  };

  const getConfidenceColor = (confidence) => {
    const colors = {
      high: 'text-green-600 bg-green-50 border-green-200',
      medium: 'text-amber-600 bg-amber-50 border-amber-200',
      low: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[confidence] || colors.medium;
  };

  const getImprovementPercentage = (before, after) => {
    return Math.round(((after - before) / before) * 100);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Interview Rate Improvement */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Interview Rate Improvement
                  <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getConfidenceColor(mockTransformationData.interviewRateImprovement.confidence)}`}>
                    {mockTransformationData.interviewRateImprovement.confidence} confidence
                  </div>
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Estimated improvement in interview callback rate
                </EnhancedCardDescription>
              </div>
              
              <div className="flex items-center gap-2">
                <select
                  value={selectedTimeframe}
                  onChange={(e) => setSelectedTimeframe(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="30days">30 Days</option>
                  <option value="60days">60 Days</option>
                  <option value="90days">90 Days</option>
                </select>
              </div>
            </div>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Before Rate */}
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-3 bg-red-100 rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-xl font-bold text-red-600">
                      {mockTransformationData.interviewRateImprovement.before}%
                    </div>
                    <div className="text-xs text-red-700">before</div>
                  </div>
                </div>
                <h4 className="font-medium text-gray-900">Previous Rate</h4>
                <p className="text-sm text-gray-600">Interview callbacks</p>
              </div>

              {/* After Rate */}
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-xl font-bold text-green-600">
                      {mockTransformationData.interviewRateImprovement.after}%
                    </div>
                    <div className="text-xs text-green-700">projected</div>
                  </div>
                </div>
                <h4 className="font-medium text-gray-900">Enhanced Rate</h4>
                <p className="text-sm text-gray-600">With improvements</p>
              </div>

              {/* Improvement */}
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-xl font-bold text-purple-600">
                      +{mockTransformationData.interviewRateImprovement.improvement}
                    </div>
                    <div className="text-xs text-purple-700">points</div>
                  </div>
                </div>
                <h4 className="font-medium text-gray-900">Improvement</h4>
                <p className="text-sm text-gray-600">
                  {getImprovementPercentage(
                    mockTransformationData.interviewRateImprovement.before,
                    mockTransformationData.interviewRateImprovement.after
                  )}% increase
                </p>
              </div>
            </div>

            {/* Detailed Projections */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-3">Projected Impact Over {selectedTimeframe}</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-700">
                    {selectedTimeframe === '30days' ? '4-6' : 
                     selectedTimeframe === '60days' ? '8-12' : '12-18'}
                  </div>
                  <div className="text-sm text-blue-600">Additional Interviews</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-700">
                    {selectedTimeframe === '30days' ? '2-3' : 
                     selectedTimeframe === '60days' ? '4-6' : '6-9'}
                  </div>
                  <div className="text-sm text-blue-600">Potential Offers</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-700">
                    ${selectedTimeframe === '30days' ? '8-15k' : 
                      selectedTimeframe === '60days' ? '12-25k' : '18-35k'}
                  </div>
                  <div className="text-sm text-blue-600">Salary Potential</div>
                </div>
              </div>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Detailed Keyword Analysis */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Detailed Keyword Analysis
              <div className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                {mockTransformationData.keywordAnalysis.relevanceScore}% relevance
              </div>
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Comprehensive analysis of keyword optimization and relevance scoring
            </EnhancedCardDescription>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Keyword Summary */}
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Keyword Summary</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Plus className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-gray-900">Keywords Added</span>
                    </div>
                    <span className="text-lg font-bold text-green-600">
                      {mockTransformationData.keywordAnalysis.totalAdded}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Minus className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-medium text-gray-900">Keywords Removed</span>
                    </div>
                    <span className="text-lg font-bold text-red-600">
                      {mockTransformationData.keywordAnalysis.totalRemoved}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-gray-900">Net Improvement</span>
                    </div>
                    <span className="text-lg font-bold text-blue-600">
                      +{mockTransformationData.keywordAnalysis.totalAdded - mockTransformationData.keywordAnalysis.totalRemoved}
                    </span>
                  </div>
                </div>
              </div>

              {/* Category Breakdown */}
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Category Breakdown</h4>
                <div className="space-y-3">
                  {Object.entries(mockTransformationData.keywordAnalysis.categories).map(([category, data]) => (
                    <div key={category} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900 capitalize">
                          {category.replace('_', ' ')}
                        </span>
                        <span className="text-sm font-bold text-blue-600">
                          +{data.added} keywords
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${data.relevance}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">{data.relevance}% relevant</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Relevance Score Visualization */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">Overall Relevance Score</h4>
                <div className="text-2xl font-bold text-blue-600">
                  {mockTransformationData.keywordAnalysis.relevanceScore}%
                </div>
              </div>
              <div className="w-full bg-white rounded-full h-3 mb-2">
                <motion.div
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${mockTransformationData.keywordAnalysis.relevanceScore}%` }}
                  transition={{ duration: 1.5, delay: 0.5 }}
                />
              </div>
              <p className="text-sm text-gray-600">
                Your resume now matches {mockTransformationData.keywordAnalysis.relevanceScore}% of job requirements
              </p>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Content Enhancement Metrics */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Content Enhancement Metrics
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Detailed statistics on content improvements and enhancements
            </EnhancedCardDescription>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {mockTransformationData.contentEnhancement.sectionsImproved}
                </div>
                <div className="text-sm text-blue-700 font-medium">Sections</div>
                <div className="text-xs text-gray-600">Improved</div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {mockTransformationData.contentEnhancement.bulletsEnhanced}
                </div>
                <div className="text-sm text-green-700 font-medium">Bullets</div>
                <div className="text-xs text-gray-600">Enhanced</div>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {mockTransformationData.contentEnhancement.metricsAdded}
                </div>
                <div className="text-sm text-purple-700 font-medium">Metrics</div>
                <div className="text-xs text-gray-600">Added</div>
              </div>
              
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <div className="text-2xl font-bold text-amber-600">
                  {mockTransformationData.contentEnhancement.actionVerbsStrengthened}
                </div>
                <div className="text-sm text-amber-700 font-medium">Action Verbs</div>
                <div className="text-xs text-gray-600">Strengthened</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Content Quality</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Word Count Change</span>
                    <span className={`font-medium ${
                      mockTransformationData.contentEnhancement.wordCountChange > 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {mockTransformationData.contentEnhancement.wordCountChange > 0 ? '+' : ''}
                      {mockTransformationData.contentEnhancement.wordCountChange} words
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Readability Score</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${mockTransformationData.contentEnhancement.readabilityScore}%` }}
                        />
                      </div>
                      <span className="font-medium text-green-600">
                        {mockTransformationData.contentEnhancement.readabilityScore}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">ATS Compatibility</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">ATS Score Improvement</span>
                    <span className="font-medium text-green-600">
                      +{mockTransformationData.atsCompatibility.improvement} points
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Pass Rate</span>
                    <span className="font-medium text-blue-600">
                      {mockTransformationData.atsCompatibility.passRate}%
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">vs Industry Benchmark</span>
                    <span className={`font-medium ${
                      mockTransformationData.atsCompatibility.afterScore > mockTransformationData.atsCompatibility.industryBenchmark
                        ? 'text-green-600'
                        : 'text-amber-600'
                    }`}>
                      {mockTransformationData.atsCompatibility.afterScore > mockTransformationData.atsCompatibility.industryBenchmark
                        ? `+${mockTransformationData.atsCompatibility.afterScore - mockTransformationData.atsCompatibility.industryBenchmark} above`
                        : `${mockTransformationData.atsCompatibility.industryBenchmark - mockTransformationData.atsCompatibility.afterScore} below`
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Exportable Analytics Reports (Pro Feature) */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <Download className="w-5 h-5" />
                  Analytics Reports
                  {!isProUser && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                      <Crown className="w-3 h-3" />
                      Pro Only
                    </div>
                  )}
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Export detailed analytics and transformation reports
                </EnhancedCardDescription>
              </div>
              
              {isProUser && (
                <div className="flex items-center gap-2">
                  <select
                    value={exportFormat}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="pdf">PDF Report</option>
                    <option value="excel">Excel Spreadsheet</option>
                    <option value="json">JSON Data</option>
                  </select>
                  
                  <Button
                    onClick={handleExportReport}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              )}
            </div>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            {isProUser ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-gray-900">Comprehensive Report</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Full analysis with before/after comparisons, keyword breakdown, and improvement recommendations
                  </p>
                  <div className="text-xs text-gray-500">
                    Includes: ATS scores, keyword analysis, content metrics, interview projections
                  </div>
                </div>
                
                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-gray-900">Data Export</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Raw data for further analysis and tracking progress over time
                  </p>
                  <div className="text-xs text-gray-500">
                    Formats: Excel, CSV, JSON for integration with other tools
                  </div>
                </div>
                
                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Award className="w-4 h-4 text-purple-600" />
                    <span className="font-medium text-gray-900">Executive Summary</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    High-level overview perfect for sharing with career coaches or mentors
                  </p>
                  <div className="text-xs text-gray-500">
                    Key metrics, improvements, and actionable insights
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center">
                  <Crown className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="font-medium text-gray-900 mb-2">Unlock Detailed Analytics</h3>
                <p className="text-gray-600 mb-4">
                  Get comprehensive reports with detailed breakdowns, exportable data, and professional summaries
                </p>
                <Button
                  onClick={onUpgradeClick}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Crown className="w-4 h-4 mr-2" />
                  Upgrade to Pro
                </Button>
              </div>
            )}
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>
    </motion.div>
  );
}/**

 * ComparisonAndPreviewTools Component
 * Subtask 7.3: Implement side-by-side comparison, highlight system, PDF preview, and download options
 */
function ComparisonAndPreviewTools({
  originalResume,
  enhancedResume,
  appliedChanges = [],
  isProUser = false,
  onUpgradeClick,
  className = ''
}) {
  const [viewMode, setViewMode] = useState('side-by-side'); // side-by-side, overlay, enhanced-only
  const [showHighlights, setShowHighlights] = useState(true);
  const [selectedSection, setSelectedSection] = useState('all');
  const [downloadFormat, setDownloadFormat] = useState('pdf');
  const [previewMode, setPreviewMode] = useState('desktop'); // desktop, mobile, print

  // Mock resume data if not provided
  const mockOriginalResume = originalResume || {
    sections: {
      contact: {
        name: "John Smith",
        email: "john.smith@email.com",
        phone: "(555) 123-4567",
        location: "San Francisco, CA"
      },
      summary: "Software engineer with experience in web development.",
      experience: [
        {
          title: "Software Engineer",
          company: "TechCorp",
          duration: "2020-2023",
          bullets: [
            "Developed web applications for clients",
            "Worked with team members on projects",
            "Fixed bugs and improved code quality"
          ]
        }
      ],
      skills: null,
      education: [
        {
          degree: "Bachelor of Science in Computer Science",
          school: "University of California",
          year: "2020"
        }
      ]
    }
  };

  const mockEnhancedResume = enhancedResume || {
    sections: {
      contact: {
        name: "John Smith",
        email: "john.smith@email.com",
        phone: "(555) 123-4567",
        location: "San Francisco, CA",
        linkedin: "linkedin.com/in/johnsmith",
        github: "github.com/johnsmith"
      },
      summary: "Senior software engineer with 5+ years building scalable React applications, leading cross-functional teams of 8+ developers, and improving system performance by 40%.",
      experience: [
        {
          title: "Senior Software Engineer",
          company: "TechCorp",
          duration: "2020-2023",
          bullets: [
            "Architected enterprise-grade React applications serving 50K+ users with 99.9% uptime, resulting in 40% performance improvement and $2M revenue impact",
            "Led cross-functional team of 8+ developers through agile development cycles, delivering 15+ features ahead of schedule",
            "Optimized legacy codebase reducing technical debt by 60% and improving maintainability scores from 3.2 to 8.7"
          ]
        }
      ],
      skills: {
        technical: ["React", "Node.js", "Python", "AWS", "Docker", "Kubernetes"],
        soft: ["Leadership", "Agile", "Team Collaboration", "Problem Solving"]
      },
      education: [
        {
          degree: "Bachelor of Science in Computer Science",
          school: "University of California",
          year: "2020",
          relevant: "Relevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems"
        }
      ]
    }
  };

  const mockAppliedChanges = appliedChanges.length > 0 ? appliedChanges : [
    {
      id: 'summary-enhancement',
      section: 'summary',
      type: 'content_enhancement',
      before: "Software engineer with experience in web development.",
      after: "Senior software engineer with 5+ years building scalable React applications, leading cross-functional teams of 8+ developers, and improving system performance by 40%.",
      keywords: ['Senior', 'scalable', 'React', 'cross-functional', 'performance'],
      impact: 12
    },
    {
      id: 'skills-addition',
      section: 'skills',
      type: 'section_addition',
      before: null,
      after: "Technical Skills: React, Node.js, Python, AWS, Docker, Kubernetes\nSoft Skills: Leadership, Agile, Team Collaboration, Problem Solving",
      keywords: ['React', 'Node.js', 'Python', 'AWS', 'Leadership', 'Agile'],
      impact: 15
    },
    {
      id: 'experience-enhancement',
      section: 'experience',
      type: 'bullet_enhancement',
      before: "Developed web applications for clients",
      after: "Architected enterprise-grade React applications serving 50K+ users with 99.9% uptime, resulting in 40% performance improvement and $2M revenue impact",
      keywords: ['Architected', 'enterprise-grade', 'React', '50K+ users', '99.9% uptime', '40% performance', '$2M revenue'],
      impact: 18
    }
  ];

  const handleDownload = (format) => {
    if (!isProUser && format !== 'pdf') {
      onUpgradeClick?.();
      return;
    }
    
    // Mock download functionality
    console.log(`Downloading resume as ${format}`);
  };

  const getChangeTypeColor = (type) => {
    const colors = {
      content_enhancement: 'bg-blue-100 border-blue-300',
      section_addition: 'bg-green-100 border-green-300',
      bullet_enhancement: 'bg-purple-100 border-purple-300',
      formatting: 'bg-amber-100 border-amber-300'
    };
    return colors[type] || 'bg-gray-100 border-gray-300';
  };

  const getChangeTypeIcon = (type) => {
    const icons = {
      content_enhancement: FileText,
      section_addition: Plus,
      bullet_enhancement: Edit3,
      formatting: Sparkles
    };
    const Icon = icons[type] || CheckCircle;
    return <Icon className="w-4 h-4" />;
  };

  const highlightChanges = (text, changes) => {
    if (!showHighlights || !changes) return text;
    
    let highlightedText = text;
    changes.forEach((change, index) => {
      if (change.keywords) {
        change.keywords.forEach(keyword => {
          const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
          highlightedText = highlightedText.replace(
            regex,
            `<mark class="bg-yellow-200 px-1 rounded" data-keyword="${keyword}">${keyword}</mark>`
          );
        });
      }
    });
    
    return highlightedText;
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Comparison Controls */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Resume Comparison & Preview
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Compare original vs enhanced resume with detailed change tracking
                </EnhancedCardDescription>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant={showHighlights ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowHighlights(!showHighlights)}
                  className="text-amber-600 border-amber-300"
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  {showHighlights ? 'Hide' : 'Show'} Highlights
                </Button>
              </div>
            </div>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            {/* View Mode Controls */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">View Mode:</span>
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  {[
                    { value: 'side-by-side', label: 'Side by Side', icon: Eye },
                    { value: 'overlay', label: 'Overlay', icon: FileText },
                    { value: 'enhanced-only', label: 'Enhanced Only', icon: Star }
                  ].map(({ value, label, icon: Icon }) => (
                    <button
                      key={value}
                      onClick={() => setViewMode(value)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-all duration-200 flex items-center gap-1 ${
                        viewMode === value
                          ? 'bg-white text-blue-600 shadow-sm'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-3 h-3" />
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Section:</span>
                <select
                  value={selectedSection}
                  onChange={(e) => setSelectedSection(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Sections</option>
                  <option value="summary">Summary</option>
                  <option value="experience">Experience</option>
                  <option value="skills">Skills</option>
                  <option value="education">Education</option>
                </select>
              </div>
            </div>

            {/* Applied Changes Summary */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-3">Applied Changes Summary</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {mockAppliedChanges.map((change, index) => (
                  <div
                    key={change.id}
                    className={`p-3 rounded-lg border-2 border-dashed ${getChangeTypeColor(change.type)}`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {getChangeTypeIcon(change.type)}
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {change.type.replace('_', ' ')}
                      </span>
                      <div className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                        +{change.impact} pts
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">
                      Section: {change.section}
                    </p>
                    {change.keywords && (
                      <div className="flex flex-wrap gap-1">
                        {change.keywords.slice(0, 3).map((keyword, idx) => (
                          <span
                            key={idx}
                            className="px-1 py-0.5 bg-yellow-100 text-yellow-800 rounded text-xs"
                          >
                            {keyword}
                          </span>
                        ))}
                        {change.keywords.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{change.keywords.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Resume Comparison View */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardContent className="p-0">
            {viewMode === 'side-by-side' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
                {/* Original Resume */}
                <div className="p-6 border-r border-gray-200">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <h3 className="font-medium text-gray-900">Original Resume</h3>
                    <div className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                      ATS Score: 67
                    </div>
                  </div>
                  
                  <div className="space-y-4 text-sm">
                    {/* Contact Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Contact Information</h4>
                      <div className="text-gray-700">
                        <div>{mockOriginalResume.sections.contact.name}</div>
                        <div>{mockOriginalResume.sections.contact.email}</div>
                        <div>{mockOriginalResume.sections.contact.phone}</div>
                        <div>{mockOriginalResume.sections.contact.location}</div>
                      </div>
                    </div>

                    {/* Summary Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Professional Summary</h4>
                      <p className="text-gray-700">{mockOriginalResume.sections.summary}</p>
                    </div>

                    {/* Experience Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Experience</h4>
                      {mockOriginalResume.sections.experience.map((exp, index) => (
                        <div key={index} className="mb-3">
                          <div className="font-medium text-gray-900">{exp.title}</div>
                          <div className="text-gray-600">{exp.company} • {exp.duration}</div>
                          <ul className="mt-2 space-y-1">
                            {exp.bullets.map((bullet, idx) => (
                              <li key={idx} className="text-gray-700">• {bullet}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>

                    {/* Skills Section (Missing) */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 text-red-600">Skills</h4>
                      <p className="text-red-600 italic">Section missing</p>
                    </div>

                    {/* Education Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Education</h4>
                      {mockOriginalResume.sections.education.map((edu, index) => (
                        <div key={index} className="text-gray-700">
                          <div className="font-medium">{edu.degree}</div>
                          <div>{edu.school} • {edu.year}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Enhanced Resume */}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <h3 className="font-medium text-gray-900">Enhanced Resume</h3>
                    <div className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                      ATS Score: 94
                    </div>
                  </div>
                  
                  <div className="space-y-4 text-sm">
                    {/* Contact Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Contact Information</h4>
                      <div className="text-gray-700">
                        <div>{mockEnhancedResume.sections.contact.name}</div>
                        <div>{mockEnhancedResume.sections.contact.email}</div>
                        <div>{mockEnhancedResume.sections.contact.phone}</div>
                        <div>{mockEnhancedResume.sections.contact.location}</div>
                        {showHighlights && (
                          <>
                            <div className="bg-green-100 px-1 rounded">
                              {mockEnhancedResume.sections.contact.linkedin}
                            </div>
                            <div className="bg-green-100 px-1 rounded">
                              {mockEnhancedResume.sections.contact.github}
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Summary Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Professional Summary</h4>
                      <p 
                        className="text-gray-700"
                        dangerouslySetInnerHTML={{
                          __html: showHighlights 
                            ? highlightChanges(mockEnhancedResume.sections.summary, mockAppliedChanges.filter(c => c.section === 'summary'))
                            : mockEnhancedResume.sections.summary
                        }}
                      />
                    </div>

                    {/* Experience Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Experience</h4>
                      {mockEnhancedResume.sections.experience.map((exp, index) => (
                        <div key={index} className="mb-3">
                          <div className="font-medium text-gray-900">{exp.title}</div>
                          <div className="text-gray-600">{exp.company} • {exp.duration}</div>
                          <ul className="mt-2 space-y-1">
                            {exp.bullets.map((bullet, idx) => (
                              <li 
                                key={idx} 
                                className="text-gray-700"
                                dangerouslySetInnerHTML={{
                                  __html: showHighlights 
                                    ? `• ${highlightChanges(bullet, mockAppliedChanges.filter(c => c.section === 'experience'))}`
                                    : `• ${bullet}`
                                }}
                              />
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>

                    {/* Skills Section (Added) */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">
                        Skills
                        {showHighlights && (
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                            NEW SECTION
                          </span>
                        )}
                      </h4>
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-800">Technical Skills: </span>
                          <span 
                            className="text-gray-700"
                            dangerouslySetInnerHTML={{
                              __html: showHighlights 
                                ? highlightChanges(mockEnhancedResume.sections.skills.technical.join(', '), mockAppliedChanges.filter(c => c.section === 'skills'))
                                : mockEnhancedResume.sections.skills.technical.join(', ')
                            }}
                          />
                        </div>
                        <div>
                          <span className="font-medium text-gray-800">Soft Skills: </span>
                          <span 
                            className="text-gray-700"
                            dangerouslySetInnerHTML={{
                              __html: showHighlights 
                                ? highlightChanges(mockEnhancedResume.sections.skills.soft.join(', '), mockAppliedChanges.filter(c => c.section === 'skills'))
                                : mockEnhancedResume.sections.skills.soft.join(', ')
                            }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Education Section */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Education</h4>
                      {mockEnhancedResume.sections.education.map((edu, index) => (
                        <div key={index} className="text-gray-700">
                          <div className="font-medium">{edu.degree}</div>
                          <div>{edu.school} • {edu.year}</div>
                          {edu.relevant && showHighlights && (
                            <div className="bg-blue-100 px-1 rounded mt-1 text-sm">
                              {edu.relevant}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {viewMode === 'enhanced-only' && (
              <div className="p-6">
                <div className="flex items-center gap-2 mb-6">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <h3 className="font-medium text-gray-900">Enhanced Resume Preview</h3>
                  <div className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                    ATS Score: 94 (+27 improvement)
                  </div>
                </div>
                
                {/* Enhanced resume content would go here - similar to above but full width */}
                <div className="max-w-4xl mx-auto bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
                  {/* Full enhanced resume layout */}
                  <div className="space-y-6">
                    {/* Contact Section */}
                    <div className="text-center border-b border-gray-200 pb-4">
                      <h1 className="text-2xl font-bold text-gray-900">{mockEnhancedResume.sections.contact.name}</h1>
                      <div className="flex items-center justify-center gap-4 mt-2 text-sm text-gray-600">
                        <span>{mockEnhancedResume.sections.contact.email}</span>
                        <span>•</span>
                        <span>{mockEnhancedResume.sections.contact.phone}</span>
                        <span>•</span>
                        <span>{mockEnhancedResume.sections.contact.location}</span>
                      </div>
                      <div className="flex items-center justify-center gap-4 mt-1 text-sm text-blue-600">
                        <span>{mockEnhancedResume.sections.contact.linkedin}</span>
                        <span>•</span>
                        <span>{mockEnhancedResume.sections.contact.github}</span>
                      </div>
                    </div>

                    {/* Professional Summary */}
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900 mb-3">Professional Summary</h2>
                      <p 
                        className="text-gray-700 leading-relaxed"
                        dangerouslySetInnerHTML={{
                          __html: showHighlights 
                            ? highlightChanges(mockEnhancedResume.sections.summary, mockAppliedChanges.filter(c => c.section === 'summary'))
                            : mockEnhancedResume.sections.summary
                        }}
                      />
                    </div>

                    {/* Skills */}
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900 mb-3">Skills</h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h3 className="font-medium text-gray-800 mb-2">Technical Skills</h3>
                          <div className="flex flex-wrap gap-2">
                            {mockEnhancedResume.sections.skills.technical.map((skill, index) => (
                              <span
                                key={index}
                                className={`px-3 py-1 rounded-full text-sm ${
                                  showHighlights ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                                }`}
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-800 mb-2">Soft Skills</h3>
                          <div className="flex flex-wrap gap-2">
                            {mockEnhancedResume.sections.skills.soft.map((skill, index) => (
                              <span
                                key={index}
                                className={`px-3 py-1 rounded-full text-sm ${
                                  showHighlights ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                                }`}
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Experience */}
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900 mb-3">Professional Experience</h2>
                      {mockEnhancedResume.sections.experience.map((exp, index) => (
                        <div key={index} className="mb-6">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-semibold text-gray-900">{exp.title}</h3>
                            <span className="text-gray-600">{exp.duration}</span>
                          </div>
                          <div className="text-gray-700 font-medium mb-3">{exp.company}</div>
                          <ul className="space-y-2">
                            {exp.bullets.map((bullet, idx) => (
                              <li 
                                key={idx} 
                                className="text-gray-700 leading-relaxed"
                                dangerouslySetInnerHTML={{
                                  __html: showHighlights 
                                    ? `• ${highlightChanges(bullet, mockAppliedChanges.filter(c => c.section === 'experience'))}`
                                    : `• ${bullet}`
                                }}
                              />
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>

                    {/* Education */}
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900 mb-3">Education</h2>
                      {mockEnhancedResume.sections.education.map((edu, index) => (
                        <div key={index}>
                          <div className="flex items-center justify-between">
                            <h3 className="font-medium text-gray-900">{edu.degree}</h3>
                            <span className="text-gray-600">{edu.year}</span>
                          </div>
                          <div className="text-gray-700">{edu.school}</div>
                          {edu.relevant && (
                            <div className={`mt-2 text-sm ${showHighlights ? 'bg-blue-100 px-2 py-1 rounded' : 'text-gray-600'}`}>
                              {edu.relevant}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Download Options */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <Download className="w-5 h-5" />
              Download Options
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Export your enhanced resume in multiple formats
            </EnhancedCardDescription>
          </EnhancedCardHeader>

          <EnhancedCardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* PDF Download */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="w-5 h-5 text-red-600" />
                  <span className="font-medium text-gray-900">PDF Format</span>
                  <div className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                    Free
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Standard PDF format compatible with all ATS systems and recruiters
                </p>
                <Button
                  onClick={() => handleDownload('pdf')}
                  className="w-full bg-red-600 hover:bg-red-700"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download PDF
                </Button>
              </div>

              {/* Word Document */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-gray-900">Word Document</span>
                  {!isProUser && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                      <Crown className="w-3 h-3" />
                      Pro
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Editable Word document for further customization and modifications
                </p>
                <Button
                  onClick={() => handleDownload('docx')}
                  disabled={!isProUser}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
                >
                  <Download className="w-4 h-4 mr-2" />
                  {isProUser ? 'Download Word' : 'Upgrade for Word'}
                </Button>
              </div>

              {/* Multiple Versions */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Star className="w-5 h-5 text-purple-600" />
                  <span className="font-medium text-gray-900">All Formats</span>
                  {!isProUser && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                      <Crown className="w-3 h-3" />
                      Pro
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  PDF, Word, and plain text versions plus comparison report
                </p>
                <Button
                  onClick={() => handleDownload('all')}
                  disabled={!isProUser}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300"
                >
                  <Download className="w-4 h-4 mr-2" />
                  {isProUser ? 'Download All' : 'Upgrade for All'}
                </Button>
              </div>
            </div>

            {/* Preview Mode Selector */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900">Preview Mode</h4>
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  {[
                    { value: 'desktop', label: 'Desktop', icon: Eye },
                    { value: 'mobile', label: 'Mobile', icon: Users },
                    { value: 'print', label: 'Print', icon: FileText }
                  ].map(({ value, label, icon: Icon }) => (
                    <button
                      key={value}
                      onClick={() => setPreviewMode(value)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-all duration-200 flex items-center gap-1 ${
                        previewMode === value
                          ? 'bg-white text-blue-600 shadow-sm'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-3 h-3" />
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              
              <p className="text-sm text-gray-600">
                Preview how your resume will appear in different contexts before downloading
              </p>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>
    </motion.div>
  );
}

// Main RealTimeImpactPreview component that combines all sub-components
function RealTimeImpactPreview({
  currentScore = 67,
  targetScore = 94,
  appliedChanges = [],
  keywordData,
  transformationData,
  originalResume,
  enhancedResume,
  isProUser = false,
  onScoreUpdate,
  onUpgradeClick,
  className = ''
}) {
  const [activeTab, setActiveTab] = useState('score-updates');
  const [isAnimating, setIsAnimating] = useState(false);

  const tabs = [
    { id: 'score-updates', label: 'Live Score Updates', icon: TrendingUp },
    { id: 'keyword-analysis', label: 'Keyword Analysis', icon: Brain },
    { id: 'job-match', label: 'Job Match Metrics', icon: Target },
    { id: 'transformation', label: 'Transformation Analytics', icon: BarChart3 },
    { id: 'comparison', label: 'Comparison & Preview', icon: Eye }
  ];

  useEffect(() => {
    // Trigger animation when score changes
    if (targetScore !== currentScore) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 2500);
      return () => clearTimeout(timer);
    }
  }, [targetScore, currentScore]);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={`space-y-6 ${className}`}
    >
      {/* Tab Navigation */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardContent className="p-0">
            <div className="flex items-center overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-all duration-200 whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'score-updates' && (
            <LiveATSScoreUpdates
              currentScore={currentScore}
              targetScore={targetScore}
              appliedChanges={appliedChanges}
              onScoreUpdate={onScoreUpdate}
              isAnimating={isAnimating}
            />
          )}

          {activeTab === 'keyword-analysis' && (
            <KeywordAnalysisVisualization
              keywordData={keywordData}
              showCategories={true}
            />
          )}

          {activeTab === 'job-match' && (
            <JobMatchImprovementMetrics
              showDetails={true}
            />
          )}

          {activeTab === 'transformation' && (
            <TransformationAnalytics
              transformationData={transformationData}
              isProUser={isProUser}
              onUpgradeClick={onUpgradeClick}
            />
          )}

          {activeTab === 'comparison' && (
            <ComparisonAndPreviewTools
              originalResume={originalResume}
              enhancedResume={enhancedResume}
              appliedChanges={appliedChanges}
              isProUser={isProUser}
              onUpgradeClick={onUpgradeClick}
            />
          )}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}

export {
  LiveATSScoreUpdates,
  KeywordAnalysisVisualization,
  JobMatchImprovementMetrics,
  TransformationAnalytics,
  ComparisonAndPreviewTools,
  RealTimeImpactPreview
};

export default RealTimeImpactPreview;