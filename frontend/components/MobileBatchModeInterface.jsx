/**
 * MobileBatchModeInterface Component
 * Mobile-first responsive design for batch mode processing
 * Implements touch-friendly controls, swipe navigation, and mobile-optimized visualizations
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, PanInfo } from 'framer-motion';
import {
  Zap,
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  Download,
  BarChart3,
  TrendingUp,
  Crown,
  Star,
  ArrowRight,
  RefreshCw,
  FileText,
  Target,
  Sparkles,
  Users,
  Award,
  ChevronLeft,
  ChevronRight,
  X,
  Info,
  ArrowLeft,
  ArrowDown,
  ArrowUp,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, slideInFromRight, slideInFromLeft } from '../lib/motion';

/**
 * MobileGlobalSettings Component
 * Touch-friendly global enhancement settings for mobile
 */
function MobileGlobalSettings({
  settings,
  onSettingsChange,
  isProUser,
  onUpgradeClick,
  disabled = false
}) {
  const [localSettings, setLocalSettings] = useState(settings);
  const [activeTab, setActiveTab] = useState('level');
  const [expandedSection, setExpandedSection] = useState(null);

  // Enhancement levels optimized for mobile display
  const enhancementLevels = [
    {
      id: 'conservative',
      name: 'Conservative',
      shortName: 'Light',
      description: 'Minimal changes, preserve structure',
      impact: '+8-12',
      color: 'green',
      icon: '🛡️',
      features: ['Keyword optimization', 'Format improvements', 'Grammar fixes']
    },
    {
      id: 'balanced',
      name: 'Balanced',
      shortName: 'Smart',
      description: 'Moderate enhancement with metrics',
      impact: '+15-20',
      color: 'blue',
      icon: '⚖️',
      features: ['Enhanced verbs', 'Quantified results', 'Industry keywords'],
      recommended: true
    },
    {
      id: 'aggressive',
      name: 'Aggressive',
      shortName: 'Max',
      description: 'Heavy rewriting for maximum impact',
      impact: '+22-27',
      color: 'purple',
      icon: '🚀',
      features: ['Complete rewrite', 'Max keywords', 'Advanced metrics']
    }
  ];

  // Auto-include sections for mobile
  const autoIncludeSections = [
    {
      id: 'summary',
      name: 'Summary',
      icon: '📝',
      impact: '+5-8',
      essential: true,
      proOnly: false
    },
    {
      id: 'skills',
      name: 'Skills',
      icon: '🛠️',
      impact: '+8-12',
      essential: true,
      proOnly: false
    },
    {
      id: 'education',
      name: 'Education',
      icon: '🎓',
      impact: '+2-4',
      essential: false,
      proOnly: false
    },
    {
      id: 'coverLetter',
      name: 'Cover Letter',
      icon: '💌',
      impact: '+10-15',
      essential: false,
      proOnly: true
    }
  ];

  const handleLevelChange = useCallback((level) => {
    const newSettings = { ...localSettings, enhancementLevel: level };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  }, [localSettings, onSettingsChange]);

  const handleSectionToggle = useCallback((sectionId) => {
    const section = autoIncludeSections.find(s => s.id === sectionId);
    
    if (section?.proOnly && !isProUser) {
      onUpgradeClick?.();
      return;
    }

    const newSections = {
      ...localSettings.autoIncludeSections,
      [sectionId]: !localSettings.autoIncludeSections[sectionId]
    };
    
    const newSettings = { ...localSettings, autoIncludeSections: newSections };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  }, [localSettings, onSettingsChange, isProUser, onUpgradeClick]);

  const getTotalImpact = () => {
    const selectedLevel = enhancementLevels.find(level => level.id === localSettings.enhancementLevel);
    let baseImpact = selectedLevel ? parseInt(selectedLevel.impact.split('-')[1]) : 15;
    let sectionImpact = 0;
    
    Object.entries(localSettings.autoIncludeSections).forEach(([sectionId, enabled]) => {
      if (enabled) {
        const section = autoIncludeSections.find(s => s.id === sectionId);
        if (section) {
          sectionImpact += parseInt(section.impact.split('-')[1]);
        }
      }
    });
    
    return baseImpact + sectionImpact;
  };

  return (
    <div className="space-y-4">
      {/* Mobile Tab Navigation */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('level')}
          className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all ${
            activeTab === 'level'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Enhancement Level
        </button>
        <button
          onClick={() => setActiveTab('sections')}
          className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all ${
            activeTab === 'sections'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Sections
        </button>
      </div>

      {/* Enhancement Level Tab */}
      <AnimatePresence mode="wait">
        {activeTab === 'level' && (
          <motion.div
            key="level"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-3"
          >
            {enhancementLevels.map((level) => {
              const isSelected = localSettings.enhancementLevel === level.id;
              
              return (
                <motion.div
                  key={level.id}
                  whileTap={{ scale: 0.98 }}
                  className={`
                    relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 active:scale-95
                    ${isSelected
                      ? `border-${level.color}-500 bg-${level.color}-50`
                      : `border-gray-200 hover:border-${level.color}-300`
                    }
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                  onClick={() => !disabled && handleLevelChange(level.id)}
                >
                  {level.recommended && (
                    <div className="absolute -top-2 -right-2">
                      <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        <Star className="w-3 h-3 inline mr-1" />
                        Best
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{level.icon}</div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{level.name}</h3>
                        <p className="text-sm text-gray-600">{level.shortName}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-green-600">{level.impact}</div>
                      <div className="text-xs text-gray-500">points</div>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{level.description}</p>

                  {/* Expandable Features */}
                  <div className="space-y-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedSection(expandedSection === level.id ? null : level.id);
                      }}
                      className="flex items-center justify-between w-full text-left"
                    >
                      <span className="text-sm font-medium text-gray-700">Features</span>
                      {expandedSection === level.id ? (
                        <ArrowUp className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ArrowDown className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                    
                    <AnimatePresence>
                      {expandedSection === level.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="space-y-1 pt-2">
                            {level.features.map((feature, index) => (
                              <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                                <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                                {feature}
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute top-4 right-4"
                    >
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-white" />
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        )}

        {/* Auto-Include Sections Tab */}
        {activeTab === 'sections' && (
          <motion.div
            key="sections"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-3"
          >
            {autoIncludeSections.map((section) => {
              const isEnabled = localSettings.autoIncludeSections[section.id];
              const canAccess = !section.proOnly || isProUser;

              return (
                <motion.div
                  key={section.id}
                  whileTap={{ scale: 0.98 }}
                  className={`
                    relative p-4 rounded-xl border-2 transition-all duration-300 active:scale-95
                    ${isEnabled && canAccess
                      ? 'border-blue-500 bg-blue-50'
                      : canAccess
                      ? 'border-gray-200 hover:border-gray-300'
                      : 'border-purple-200 bg-purple-50 opacity-75'
                    }
                    ${canAccess && !disabled ? 'cursor-pointer' : 'cursor-not-allowed'}
                  `}
                  onClick={() => canAccess && !disabled && handleSectionToggle(section.id)}
                >
                  {section.proOnly && (
                    <div className="absolute -top-2 -right-2">
                      <TierBadge tier="pro" size="sm" animated={true} />
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{section.icon}</div>
                      <div>
                        <h4 className="font-medium text-gray-900">{section.name}</h4>
                        <div className="text-sm font-medium text-green-600">{section.impact} pts</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {!canAccess && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onUpgradeClick?.();
                          }}
                          className="text-xs border-purple-300 text-purple-700 hover:bg-purple-50"
                        >
                          Upgrade
                        </Button>
                      )}
                      
                      {canAccess && (
                        <div className={`
                          w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all
                          ${isEnabled
                            ? 'bg-blue-500 border-blue-500'
                            : 'border-gray-300 hover:border-blue-400'
                          }
                        `}>
                          {isEnabled && <CheckCircle className="w-5 h-5 text-white" />}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Total Impact</h4>
            <div className="text-sm text-gray-600">
              {Object.values(localSettings.autoIncludeSections).filter(Boolean).length} sections enabled
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">+{getTotalImpact()}</div>
            <div className="text-sm text-gray-600">points</div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * MobileProcessingVisualization Component
 * Touch-optimized processing visualization with swipe navigation
 */
function MobileProcessingVisualization({
  jobs,
  currentJobIndex,
  overallProgress,
  isProcessing,
  onJobSelect,
  estimatedTimeRemaining
}) {
  const [viewMode, setViewMode] = useState('current'); // 'current', 'queue', 'overview'
  const containerRef = useRef(null);
  const x = useMotionValue(0);

  const currentJob = jobs[currentJobIndex];
  const completedJobs = jobs.filter(job => job.status === 'completed').length;
  const totalJobs = jobs.length;

  const handleSwipeEnd = (event, info) => {
    const threshold = 50;
    
    if (info.offset.x > threshold && viewMode !== 'current') {
      // Swipe right - go to previous view
      if (viewMode === 'overview') setViewMode('queue');
      else if (viewMode === 'queue') setViewMode('current');
    } else if (info.offset.x < -threshold && viewMode !== 'overview') {
      // Swipe left - go to next view
      if (viewMode === 'current') setViewMode('queue');
      else if (viewMode === 'queue') setViewMode('overview');
    }
    
    x.set(0);
  };

  const getViewIndex = () => {
    switch (viewMode) {
      case 'current': return 0;
      case 'queue': return 1;
      case 'overview': return 2;
      default: return 0;
    }
  };

  return (
    <div className="space-y-4">
      {/* View Mode Tabs */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        {[
          { id: 'current', label: 'Current', icon: Target },
          { id: 'queue', label: 'Queue', icon: Clock },
          { id: 'overview', label: 'Overview', icon: BarChart3 }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setViewMode(id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all ${
              viewMode === id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Swipeable Content */}
      <div className="relative overflow-hidden rounded-xl">
        <motion.div
          ref={containerRef}
          className="flex"
          style={{ x }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.2}
          onDragEnd={handleSwipeEnd}
          animate={{ x: -getViewIndex() * 100 + '%' }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {/* Current Job View */}
          <div className="w-full flex-shrink-0">
            <EnhancedCard>
              <EnhancedCardHeader>
                <div className="flex items-center justify-between">
                  <EnhancedCardTitle className="text-lg">
                    Current Job
                  </EnhancedCardTitle>
                  <div className="text-sm text-gray-500">
                    {currentJobIndex + 1} of {totalJobs}
                  </div>
                </div>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                {currentJob ? (
                  <div className="space-y-4">
                    <div className="text-center">
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {currentJob.jobTitle}
                      </h3>
                      <div className="text-sm text-gray-600 mb-4">
                        {currentJob.company}
                      </div>
                    </div>

                    {/* Progress Steps */}
                    <div className="space-y-3">
                      {currentJob.steps?.map((step, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                            ${step.status === 'completed' ? 'bg-green-500 text-white' :
                              step.status === 'active' ? 'bg-blue-500 text-white' :
                              'bg-gray-200 text-gray-600'}
                          `}>
                            {step.status === 'completed' ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : step.status === 'active' ? (
                              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            ) : (
                              index + 1
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                              {step.name}
                            </div>
                            {step.duration && (
                              <div className="text-xs text-gray-500">
                                {step.duration}s
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Time Remaining */}
                    {estimatedTimeRemaining && (
                      <div className="bg-blue-50 rounded-lg p-3 text-center">
                        <div className="text-sm text-blue-600 font-medium">
                          Estimated time remaining
                        </div>
                        <div className="text-lg font-bold text-blue-700">
                          {estimatedTimeRemaining}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-gray-500">No job currently processing</div>
                  </div>
                )}
              </EnhancedCardContent>
            </EnhancedCard>
          </div>

          {/* Queue View */}
          <div className="w-full flex-shrink-0 px-4">
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg">
                  Processing Queue
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-3">
                  {jobs.map((job, index) => (
                    <motion.div
                      key={job.id}
                      whileTap={{ scale: 0.98 }}
                      className={`
                        p-3 rounded-lg border-2 cursor-pointer transition-all active:scale-95
                        ${job.status === 'completed' ? 'border-green-200 bg-green-50' :
                          job.status === 'processing' ? 'border-blue-200 bg-blue-50' :
                          job.status === 'failed' ? 'border-red-200 bg-red-50' :
                          'border-gray-200 bg-gray-50'}
                      `}
                      onClick={() => onJobSelect?.(index)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`
                            w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
                            ${job.status === 'completed' ? 'bg-green-500 text-white' :
                              job.status === 'processing' ? 'bg-blue-500 text-white' :
                              job.status === 'failed' ? 'bg-red-500 text-white' :
                              'bg-gray-300 text-gray-600'}
                          `}>
                            {job.status === 'completed' ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : job.status === 'processing' ? (
                              <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                            ) : job.status === 'failed' ? (
                              <X className="w-4 h-4" />
                            ) : (
                              index + 1
                            )}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900 truncate">
                              {job.jobTitle}
                            </div>
                            <div className="text-xs text-gray-500">
                              {job.company}
                            </div>
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {job.status === 'completed' && job.completionTime && (
                            `${Math.round((job.completionTime - job.startTime) / 1000)}s`
                          )}
                          {job.status === 'processing' && job.estimatedTime && (
                            `~${job.estimatedTime}s`
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </div>

          {/* Overview View */}
          <div className="w-full flex-shrink-0 px-8">
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg">
                  Batch Overview
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-4">
                  {/* Progress Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{completedJobs}</div>
                      <div className="text-xs text-gray-600">Completed</div>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {jobs.filter(job => job.status === 'processing').length}
                      </div>
                      <div className="text-xs text-gray-600">Processing</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-600">
                        {jobs.filter(job => job.status === 'queued').length}
                      </div>
                      <div className="text-xs text-gray-600">Queued</div>
                    </div>
                  </div>

                  {/* Overall Progress Bar */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                      <span className="text-sm text-gray-600">{Math.round(overallProgress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <motion.div
                        className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${overallProgress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>

                  {/* Processing Controls */}
                  <div className="flex items-center justify-center gap-3 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!isProcessing}
                      className="flex items-center gap-2"
                    >
                      <Pause className="w-4 h-4" />
                      Pause
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Retry Failed
                    </Button>
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </div>
        </motion.div>
      </div>

      {/* View Indicators */}
      <div className="flex justify-center gap-2">
        {['current', 'queue', 'overview'].map((view, index) => (
          <button
            key={view}
            onClick={() => setViewMode(view)}
            className={`
              w-2 h-2 rounded-full transition-all duration-300 active:scale-90
              ${viewMode === view
                ? 'bg-blue-500 scale-125'
                : 'bg-gray-300 hover:bg-gray-400'}
            `}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * MobileBatchResults Component
 * Mobile-friendly results overview with swipe navigation
 */
function MobileBatchResults({
  results,
  onDownload,
  onViewDetails,
  onBackToSettings
}) {
  const [selectedResult, setSelectedResult] = useState(0);
  const [viewMode, setViewMode] = useState('summary'); // 'summary', 'details', 'analytics'

  const totalJobs = results.length;
  const avgScoreImprovement = results.reduce((sum, result) => sum + result.scoreImprovement, 0) / totalJobs;
  const totalKeywordsAdded = results.reduce((sum, result) => sum + result.keywordsAdded, 0);

  return (
    <div className="space-y-4">
      {/* Results Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Batch Complete! 🎉
        </h2>
        <p className="text-gray-600">
          Successfully processed {totalJobs} job{totalJobs !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-xl font-bold text-green-600">+{Math.round(avgScoreImprovement)}</div>
          <div className="text-xs text-gray-600">Avg Score Boost</div>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-xl font-bold text-blue-600">{totalKeywordsAdded}</div>
          <div className="text-xs text-gray-600">Keywords Added</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-xl font-bold text-purple-600">{totalJobs}</div>
          <div className="text-xs text-gray-600">Jobs Processed</div>
        </div>
      </div>

      {/* Results List */}
      <div className="space-y-3">
        {results.map((result, index) => (
          <motion.div
            key={result.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl border border-gray-200 p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-gray-900 truncate">
                  {result.jobTitle}
                </h3>
                <p className="text-sm text-gray-600">{result.company}</p>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-green-600">
                  +{result.scoreImprovement}
                </div>
                <div className="text-xs text-gray-500">points</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>{result.keywordsAdded} keywords</span>
                <span>•</span>
                <span>{result.processingTime}s</span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewDetails(result.id)}
                  className="text-xs"
                >
                  View
                </Button>
                <Button
                  size="sm"
                  onClick={() => onDownload(result.id)}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Download className="w-3 h-3 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-3 pt-4">
        <Button
          onClick={() => onDownload('all')}
          className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
        >
          <Download className="w-5 h-5 mr-2" />
          Download All Results
        </Button>
        
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={onBackToSettings}
            className="flex-1"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            New Batch
          </Button>
          <Button
            variant="outline"
            onClick={() => {/* Navigate to precision mode */}}
            className="flex-1"
          >
            <Settings className="w-4 h-4 mr-2" />
            Precision Mode
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Main MobileBatchModeInterface Component
 */
export function MobileBatchModeInterface({
  resumeData,
  jobUrls = [],
  onProcessingStart,
  onProcessingComplete,
  onBackToModeSelection,
  onUpgradeClick,
  isProUser,
  maxJobs,
  className = ''
}) {
  const { user, tier, weeklyUsage, weeklyLimit } = useUserStore();
  const { processing, setProcessing } = useProcessingStore();
  const { mobileUI, updateMobileUI } = useUIStore();

  const [currentStep, setCurrentStep] = useState('settings'); // 'settings', 'processing', 'results'
  const [settings, setSettings] = useState({
    enhancementLevel: 'balanced',
    autoIncludeSections: {
      summary: true,
      skills: true,
      education: false,
      coverLetter: false
    }
  });
  const [processingJobs, setProcessingJobs] = useState([]);
  const [results, setResults] = useState([]);

  const jobCount = jobUrls.length;
  const canProcess = weeklyUsage < weeklyLimit && jobCount <= maxJobs;

  const handleStartProcessing = useCallback(() => {
    setCurrentStep('processing');
    
    // Initialize processing jobs
    const jobs = jobUrls.slice(0, maxJobs).map((url, index) => ({
      id: `job-${index}`,
      jobUrl: url,
      jobTitle: `Job ${index + 1}`, // This would come from job scraping
      company: 'Company Name',
      status: 'queued',
      progress: 0,
      steps: [
        { name: 'Analyzing job', status: 'pending' },
        { name: 'Enhancing resume', status: 'pending' },
        { name: 'Optimizing keywords', status: 'pending' },
        { name: 'Generating output', status: 'pending' }
      ],
      startTime: Date.now(),
      estimatedTime: 45
    }));
    
    setProcessingJobs(jobs);
    onProcessingStart?.(settings);
  }, [settings, jobUrls, maxJobs, onProcessingStart]);

  const handleProcessingComplete = useCallback((results) => {
    setCurrentStep('results');
    setResults(results);
    onProcessingComplete?.(results);
  }, [onProcessingComplete]);

  const handleBackToSettings = useCallback(() => {
    setCurrentStep('settings');
    setProcessingJobs([]);
    setResults([]);
  }, []);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Progress Indicator */}
      <div className="flex items-center justify-center gap-2">
        {['settings', 'processing', 'results'].map((step, index) => (
          <React.Fragment key={step}>
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all
              ${currentStep === step
                ? 'bg-blue-500 text-white'
                : index < ['settings', 'processing', 'results'].indexOf(currentStep)
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-600'}
            `}>
              {index < ['settings', 'processing', 'results'].indexOf(currentStep) ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                index + 1
              )}
            </div>
            {index < 2 && (
              <div className={`
                w-8 h-0.5 transition-all
                ${index < ['settings', 'processing', 'results'].indexOf(currentStep)
                  ? 'bg-green-500'
                  : 'bg-gray-200'}
              `} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait">
        {currentStep === 'settings' && (
          <motion.div
            key="settings"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Batch Settings
              </h2>
              <p className="text-gray-600">
                Configure global settings for {jobCount} job{jobCount !== 1 ? 's' : ''}
              </p>
            </div>

            <MobileGlobalSettings
              settings={settings}
              onSettingsChange={setSettings}
              isProUser={isProUser}
              onUpgradeClick={onUpgradeClick}
            />

            <div className="flex flex-col gap-3">
              <Button
                onClick={handleStartProcessing}
                disabled={!canProcess}
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white disabled:opacity-50"
              >
                <Play className="w-5 h-5 mr-2" />
                Start Processing {Math.min(jobCount, maxJobs)} Job{Math.min(jobCount, maxJobs) !== 1 ? 's' : ''}
              </Button>
              
              <Button
                variant="outline"
                onClick={onBackToModeSelection}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Mode Selection
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'processing' && (
          <motion.div
            key="processing"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Processing Jobs
              </h2>
              <p className="text-gray-600">
                Enhancing your resumes with AI optimization
              </p>
            </div>

            <MobileProcessingVisualization
              jobs={processingJobs}
              currentJobIndex={0}
              overallProgress={45}
              isProcessing={true}
              estimatedTimeRemaining="2:30"
            />
          </motion.div>
        )}

        {currentStep === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <MobileBatchResults
              results={results}
              onDownload={(id) => console.log('Download:', id)}
              onViewDetails={(id) => console.log('View details:', id)}
              onBackToSettings={handleBackToSettings}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default MobileBatchModeInterface;