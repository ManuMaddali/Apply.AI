/**
 * MobilePrecisionModeInterface Component
 * Mobile-first responsive design for precision mode processing
 * Implements condensed enhancement options, swipe navigation, and touch-friendly analytics
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, PanInfo } from 'framer-motion';
import {
  Settings,
  Target,
  BarChart3,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  X,
  Info,
  Edit3,
  Eye,
  Zap,
  Star,
  Crown,
  Sparkles,
  FileText,
  Award,
  Maximize2,
  Minimize2,
  RotateCcw,
  Download,
  Share2
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, slideInFromRight, slideInFromLeft } from '../lib/motion';

/**
 * MobileResumeAnalysisDashboard Component
 * Touch-optimized resume analysis with expandable sections
 */
function MobileResumeAnalysisDashboard({
  resumeData,
  jobData,
  currentScore,
  potentialScore,
  sectionScores,
  onSectionSelect
}) {
  const [expandedSection, setExpandedSection] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'sections', 'keywords'

  const improvement = potentialScore - currentScore;
  const improvementPercentage = Math.round((improvement / currentScore) * 100);

  const sections = [
    {
      id: 'contact',
      name: 'Contact Info',
      icon: '📞',
      score: sectionScores?.contact || 100,
      status: 'perfect',
      description: 'Complete and professional'
    },
    {
      id: 'summary',
      name: 'Summary',
      icon: '📝',
      score: sectionScores?.summary || 45,
      status: 'needs-keywords',
      description: 'Missing key industry terms',
      improvements: ['Add technical keywords', 'Quantify achievements', 'Strengthen opening']
    },
    {
      id: 'experience',
      name: 'Experience',
      icon: '💼',
      score: sectionScores?.experience || 78,
      status: 'good-can-enhance',
      description: 'Good foundation, can be enhanced',
      improvements: ['Add metrics to bullets', 'Use stronger action verbs', 'Include relevant technologies']
    },
    {
      id: 'skills',
      name: 'Skills',
      icon: '🛠️',
      score: sectionScores?.skills || 0,
      status: 'missing',
      description: 'Section not found',
      improvements: ['Add technical skills', 'Include soft skills', 'Match job requirements']
    },
    {
      id: 'education',
      name: 'Education',
      icon: '🎓',
      score: sectionScores?.education || 65,
      status: 'basic-format',
      description: 'Basic formatting, could be enhanced',
      improvements: ['Add relevant coursework', 'Include GPA if strong', 'Highlight honors']
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'perfect': return 'text-green-600 bg-green-50 border-green-200';
      case 'good-can-enhance': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'needs-keywords': return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'missing': return 'text-red-600 bg-red-50 border-red-200';
      case 'basic-format': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'perfect': return <CheckCircle className="w-4 h-4" />;
      case 'good-can-enhance': return <TrendingUp className="w-4 h-4" />;
      case 'needs-keywords': return <Target className="w-4 h-4" />;
      case 'missing': return <X className="w-4 h-4" />;
      case 'basic-format': return <Edit3 className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* View Mode Tabs */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'sections', label: 'Sections', icon: FileText },
          { id: 'keywords', label: 'Keywords', icon: Target }
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

      {/* Content Views */}
      <AnimatePresence mode="wait">
        {viewMode === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-4"
          >
            {/* Score Overview */}
            <EnhancedCard>
              <EnhancedCardContent className="p-6">
                <div className="text-center space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Current ATS Score
                    </h3>
                    <div className="relative">
                      <div className="text-4xl font-bold text-blue-600 mb-2">
                        {currentScore}
                      </div>
                      <div className="text-sm text-gray-600">out of 100</div>
                    </div>
                  </div>

                  {/* Score Visualization */}
                  <div className="relative w-32 h-32 mx-auto">
                    <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                      />
                      <motion.circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${2 * Math.PI * 50}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
                        animate={{ 
                          strokeDashoffset: 2 * Math.PI * 50 * (1 - currentScore / 100)
                        }}
                        transition={{ duration: 1, delay: 0.5 }}
                      />
                    </svg>
                  </div>

                  {/* Improvement Potential */}
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Potential with Pro</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-2xl font-bold text-green-600">
                        {potentialScore}
                      </span>
                      <ArrowRight className="w-4 h-4 text-gray-400" />
                      <span className="text-lg font-semibold text-blue-600">
                        +{improvement} points
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {improvementPercentage}% improvement potential
                    </div>
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-blue-600">
                  {sections.filter(s => s.score >= 80).length}
                </div>
                <div className="text-xs text-gray-600">Strong Sections</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-amber-600">
                  {sections.filter(s => s.score < 50).length}
                </div>
                <div className="text-xs text-gray-600">Need Attention</div>
              </div>
            </div>
          </motion.div>
        )}

        {viewMode === 'sections' && (
          <motion.div
            key="sections"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-3"
          >
            {sections.map((section) => (
              <motion.div
                key={section.id}
                whileTap={{ scale: 0.98 }}
                className={`
                  border-2 rounded-xl p-4 cursor-pointer transition-all active:scale-95
                  ${getStatusColor(section.status)}
                `}
                onClick={() => onSectionSelect?.(section.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">{section.icon}</div>
                    <div>
                      <h4 className="font-medium text-gray-900">{section.name}</h4>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(section.status)}
                        <span className="text-sm">{section.description}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">{section.score}</div>
                    <div className="text-xs text-gray-500">/ 100</div>
                  </div>
                </div>

                {/* Expandable Improvements */}
                {section.improvements && (
                  <div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedSection(
                          expandedSection === section.id ? null : section.id
                        );
                      }}
                      className="flex items-center justify-between w-full text-left mb-2"
                    >
                      <span className="text-sm font-medium text-gray-700">
                        Improvements ({section.improvements.length})
                      </span>
                      {expandedSection === section.id ? (
                        <ArrowUp className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ArrowDown className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                    
                    <AnimatePresence>
                      {expandedSection === section.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="space-y-2 pt-2">
                            {section.improvements.map((improvement, index) => (
                              <div key={index} className="flex items-center gap-2 text-xs">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                                <span className="text-gray-700">{improvement}</span>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}

        {viewMode === 'keywords' && (
          <motion.div
            key="keywords"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {/* Missing Keywords */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg flex items-center gap-2">
                  <Target className="w-5 h-5 text-red-500" />
                  Missing Keywords
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="flex flex-wrap gap-2">
                  {['React', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes'].map((keyword) => (
                    <div
                      key={keyword}
                      className="px-3 py-1 bg-red-50 border border-red-200 rounded-full text-sm text-red-700"
                    >
                      {keyword}
                    </div>
                  ))}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>

            {/* Existing Keywords */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Found Keywords
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="flex flex-wrap gap-2">
                  {['JavaScript', 'HTML', 'CSS', 'Git', 'Agile', 'Team Leadership'].map((keyword) => (
                    <div
                      key={keyword}
                      className="px-3 py-1 bg-green-50 border border-green-200 rounded-full text-sm text-green-700"
                    >
                      {keyword}
                    </div>
                  ))}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * MobileEnhancementOptions Component
 * Swipeable enhancement options with touch-friendly controls
 */
function MobileEnhancementOptions({
  enhancements,
  onEnhancementToggle,
  onEnhancementPreview,
  isProUser,
  onUpgradeClick
}) {
  const [activeCategory, setActiveCategory] = useState('high');
  const [selectedEnhancement, setSelectedEnhancement] = useState(null);

  const categories = [
    { id: 'high', name: 'High Impact', color: 'red', icon: '🔥' },
    { id: 'medium', name: 'Medium', color: 'amber', icon: '⚡' },
    { id: 'advanced', name: 'Advanced', color: 'purple', icon: '🚀' }
  ];

  const getEnhancementsByCategory = (category) => {
    return enhancements.filter(e => e.category === category);
  };

  const getImpactColor = (impact) => {
    if (impact >= 15) return 'text-red-600 bg-red-50';
    if (impact >= 8) return 'text-amber-600 bg-amber-50';
    return 'text-blue-600 bg-blue-50';
  };

  return (
    <div className="space-y-4">
      {/* Category Tabs */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setActiveCategory(category.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all ${
              activeCategory === category.id
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span className="text-base">{category.icon}</span>
            {category.name}
          </button>
        ))}
      </div>

      {/* Enhancement Cards */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeCategory}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="space-y-3"
        >
          {getEnhancementsByCategory(activeCategory).map((enhancement) => {
            const canAccess = enhancement.available && (!enhancement.proOnly || isProUser);
            const isSelected = selectedEnhancement === enhancement.id;

            return (
              <motion.div
                key={enhancement.id}
                whileTap={{ scale: 0.98 }}
                className={`
                  relative border-2 rounded-xl p-4 transition-all active:scale-95
                  ${canAccess
                    ? isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 cursor-pointer'
                    : 'border-purple-200 bg-purple-50 opacity-75 cursor-not-allowed'
                  }
                `}
                onClick={() => {
                  if (canAccess) {
                    setSelectedEnhancement(isSelected ? null : enhancement.id);
                  } else if (enhancement.proOnly) {
                    onUpgradeClick?.();
                  }
                }}
              >
                {enhancement.proOnly && (
                  <div className="absolute -top-2 -right-2">
                    <TierBadge tier="pro" size="sm" animated={true} />
                  </div>
                )}

                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">
                      {enhancement.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {enhancement.description}
                    </p>
                  </div>
                  <div className={`
                    px-2 py-1 rounded-full text-xs font-medium ml-3
                    ${getImpactColor(enhancement.impact)}
                  `}>
                    +{enhancement.impact}
                  </div>
                </div>

                {/* Preview Text */}
                {enhancement.previewText && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <div className="text-xs text-gray-500 mb-1">Preview:</div>
                    <div className="text-sm text-gray-700 italic">
                      "{enhancement.previewText}"
                    </div>
                  </div>
                )}

                {/* Keywords */}
                {enhancement.keywords && enhancement.keywords.length > 0 && (
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">Keywords added:</div>
                    <div className="flex flex-wrap gap-1">
                      {enhancement.keywords.slice(0, 3).map((keyword) => (
                        <span
                          key={keyword}
                          className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                        >
                          {keyword}
                        </span>
                      ))}
                      {enhancement.keywords.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{enhancement.keywords.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center gap-2">
                  {canAccess ? (
                    <>
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEnhancementToggle(enhancement.id);
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Apply
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEnhancementPreview(enhancement.id);
                        }}
                        className="flex-1"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Preview
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onUpgradeClick?.();
                      }}
                      className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white"
                    >
                      <Crown className="w-4 h-4 mr-2" />
                      Upgrade for Access
                    </Button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

/**
 * MobileBulletEnhancementInterface Component
 * Touch-friendly bullet-by-bullet enhancement with swipe navigation
 */
function MobileBulletEnhancementInterface({
  experienceSection,
  currentBulletIndex,
  onBulletChange,
  onEnhancementApply,
  isProUser,
  onUpgradeClick
}) {
  const [enhancementLevel, setEnhancementLevel] = useState('medium');
  const [showComparison, setShowComparison] = useState(false);

  const bullets = experienceSection?.bullets || [];
  const currentBullet = bullets[currentBulletIndex];

  const enhancementLevels = [
    {
      id: 'light',
      name: 'Light',
      icon: '🌱',
      impact: '+5',
      description: 'Minimal changes, preserve tone',
      color: 'green'
    },
    {
      id: 'medium',
      name: 'Medium',
      icon: '⚡',
      impact: '+12',
      description: 'Balanced enhancement with metrics',
      color: 'blue'
    },
    {
      id: 'heavy',
      name: 'Heavy',
      icon: '🚀',
      impact: '+20',
      description: 'Maximum impact rewrite',
      color: 'purple'
    }
  ];

  const getEnhancedText = (level) => {
    const examples = {
      light: "Developed responsive web applications for enterprise clients using modern frameworks",
      medium: "Engineered scalable React applications for 15+ enterprise clients, improving load times by 60%",
      heavy: "Architected enterprise-grade React applications serving 50K+ users with 99.9% uptime, resulting in 40% performance improvement and $2M revenue impact"
    };
    return examples[level] || currentBullet?.original;
  };

  return (
    <div className="space-y-4">
      {/* Bullet Navigation */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
        <button
          onClick={() => onBulletChange(Math.max(0, currentBulletIndex - 1))}
          disabled={currentBulletIndex === 0}
          className="p-2 rounded-full hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">
            Bullet {currentBulletIndex + 1} of {bullets.length}
          </div>
          <div className="text-xs text-gray-600">
            {experienceSection?.jobTitle}
          </div>
        </div>
        
        <button
          onClick={() => onBulletChange(Math.min(bullets.length - 1, currentBulletIndex + 1))}
          disabled={currentBulletIndex === bullets.length - 1}
          className="p-2 rounded-full hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Original Text */}
      <EnhancedCard>
        <EnhancedCardHeader>
          <EnhancedCardTitle className="text-lg flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Original Text
          </EnhancedCardTitle>
        </EnhancedCardHeader>
        <EnhancedCardContent>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700 leading-relaxed">
              {currentBullet?.original || "Developed web applications for clients"}
            </p>
          </div>
        </EnhancedCardContent>
      </EnhancedCard>

      {/* Enhancement Level Selection */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Choose Enhancement Level</h3>
        {enhancementLevels.map((level) => {
          const isSelected = enhancementLevel === level.id;
          const canAccess = level.id !== 'heavy' || isProUser;

          return (
            <motion.div
              key={level.id}
              whileTap={{ scale: 0.98 }}
              className={`
                relative border-2 rounded-xl p-4 cursor-pointer transition-all active:scale-95
                ${isSelected
                  ? `border-${level.color}-500 bg-${level.color}-50`
                  : canAccess
                  ? `border-gray-200 hover:border-${level.color}-300`
                  : 'border-purple-200 bg-purple-50 opacity-75 cursor-not-allowed'
                }
              `}
              onClick={() => {
                if (canAccess) {
                  setEnhancementLevel(level.id);
                } else {
                  onUpgradeClick?.();
                }
              }}
            >
              {!canAccess && (
                <div className="absolute -top-2 -right-2">
                  <TierBadge tier="pro" size="sm" animated={true} />
                </div>
              )}

              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{level.icon}</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{level.name}</h4>
                    <p className="text-sm text-gray-600">{level.description}</p>
                  </div>
                </div>
                <div className={`
                  px-2 py-1 rounded-full text-sm font-medium
                  ${isSelected ? `text-${level.color}-700 bg-${level.color}-100` : 'text-gray-600 bg-gray-100'}
                `}>
                  {level.impact}
                </div>
              </div>

              {/* Enhanced Text Preview */}
              <div className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs text-gray-500 mb-2">Enhanced version:</div>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {getEnhancedText(level.id)}
                </p>
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
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-3">
        <Button
          onClick={() => onEnhancementApply(currentBulletIndex, enhancementLevel)}
          className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
        >
          <Zap className="w-5 h-5 mr-2" />
          Apply {enhancementLevels.find(l => l.id === enhancementLevel)?.name} Enhancement
        </Button>
        
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => setShowComparison(!showComparison)}
            className="flex-1"
          >
            <Eye className="w-4 h-4 mr-2" />
            Compare
          </Button>
          <Button
            variant="outline"
            onClick={() => {/* Custom edit */}}
            className="flex-1"
          >
            <Edit3 className="w-4 h-4 mr-2" />
            Custom Edit
          </Button>
        </div>
      </div>

      {/* Comparison View */}
      <AnimatePresence>
        {showComparison && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg">
                  Before vs After Comparison
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Before:</div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-gray-700 text-sm">
                        {currentBullet?.original}
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">After:</div>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-gray-700 text-sm">
                        {getEnhancedText(enhancementLevel)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-sm font-medium text-blue-800 mb-1">
                      Improvements:
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm text-blue-700">
                        <CheckCircle className="w-3 h-3" />
                        Added quantified metrics
                      </div>
                      <div className="flex items-center gap-2 text-sm text-blue-700">
                        <CheckCircle className="w-3 h-3" />
                        Stronger action verbs
                      </div>
                      <div className="flex items-center gap-2 text-sm text-blue-700">
                        <CheckCircle className="w-3 h-3" />
                        Industry keywords
                      </div>
                    </div>
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * MobileAnalyticsDisplay Component
 * Touch-friendly analytics and scoring displays
 */
function MobileAnalyticsDisplay({
  currentScore,
  targetScore,
  appliedChanges,
  keywordAnalysis,
  transformationMetrics
}) {
  const [activeTab, setActiveTab] = useState('score');
  const [expandedMetric, setExpandedMetric] = useState(null);

  const scoreImprovement = targetScore - currentScore;
  const improvementPercentage = Math.round((scoreImprovement / currentScore) * 100);

  const tabs = [
    { id: 'score', label: 'Score', icon: Target },
    { id: 'keywords', label: 'Keywords', icon: Sparkles },
    { id: 'metrics', label: 'Metrics', icon: BarChart3 }
  ];

  return (
    <div className="space-y-4">
      {/* Tab Navigation */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all ${
              activeTab === id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'score' && (
          <motion.div
            key="score"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-4"
          >
            {/* Score Progress */}
            <EnhancedCard>
              <EnhancedCardContent className="p-6">
                <div className="text-center space-y-4">
                  <div className="flex items-center justify-center gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-600">{currentScore}</div>
                      <div className="text-xs text-gray-500">Current</div>
                    </div>
                    <ArrowRight className="w-6 h-6 text-gray-400" />
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{targetScore}</div>
                      <div className="text-xs text-gray-500">Target</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4">
                    <div className="text-lg font-bold text-green-600">
                      +{scoreImprovement} points
                    </div>
                    <div className="text-sm text-gray-600">
                      {improvementPercentage}% improvement
                    </div>
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>

            {/* Applied Changes */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg">
                  Applied Changes ({appliedChanges?.length || 0})
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-2">
                  {appliedChanges?.slice(0, 3).map((change, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">{change.title}</span>
                      <span className="text-sm font-medium text-green-600">
                        +{change.impact}
                      </span>
                    </div>
                  )) || (
                    <div className="text-center text-gray-500 py-4">
                      No changes applied yet
                    </div>
                  )}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}

        {activeTab === 'keywords' && (
          <motion.div
            key="keywords"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {/* Keywords Added */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-green-500" />
                  Keywords Added ({keywordAnalysis?.added?.length || 0})
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="flex flex-wrap gap-2">
                  {keywordAnalysis?.added?.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-green-50 border border-green-200 rounded-full text-sm text-green-700"
                    >
                      {keyword}
                    </span>
                  )) || (
                    <div className="text-center text-gray-500 py-4 w-full">
                      No keywords added yet
                    </div>
                  )}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>

            {/* Keyword Categories */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg">
                  Keyword Categories
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-3">
                  {[
                    { name: 'Technical Skills', count: 8, color: 'blue' },
                    { name: 'Soft Skills', count: 4, color: 'green' },
                    { name: 'Industry Terms', count: 6, color: 'purple' }
                  ].map((category) => (
                    <div key={category.name} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{category.name}</span>
                      <div className={`
                        px-2 py-1 rounded-full text-xs font-medium
                        text-${category.color}-700 bg-${category.color}-50
                      `}>
                        {category.count}
                      </div>
                    </div>
                  ))}
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}

        {activeTab === 'metrics' && (
          <motion.div
            key="metrics"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {/* Transformation Metrics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-blue-600">
                  {transformationMetrics?.contentEnhanced || 0}
                </div>
                <div className="text-xs text-gray-600">Sections Enhanced</div>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-green-600">
                  {transformationMetrics?.metricsAdded || 0}
                </div>
                <div className="text-xs text-gray-600">Metrics Added</div>
              </div>
            </div>

            {/* Estimated Impact */}
            <EnhancedCard>
              <EnhancedCardHeader>
                <EnhancedCardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  Estimated Impact
                </EnhancedCardTitle>
              </EnhancedCardHeader>
              <EnhancedCardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Interview Rate Improvement</span>
                    <span className="text-lg font-bold text-green-600">
                      +{transformationMetrics?.estimatedInterviewRateImprovement || 45}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                      style={{ width: `${transformationMetrics?.estimatedInterviewRateImprovement || 45}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-500 text-center">
                    Based on industry benchmarks and ATS optimization
                  </div>
                </div>
              </EnhancedCardContent>
            </EnhancedCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Main MobilePrecisionModeInterface Component
 */
export function MobilePrecisionModeInterface({
  resumeData,
  jobData,
  onEnhancementApply,
  onScoreUpdate,
  onBackToModeSelection,
  onUpgradeClick,
  isProUser,
  className = ''
}) {
  const { user, tier } = useUserStore();
  const { processing, setProcessing } = useProcessingStore();
  const { mobileUI, updateMobileUI } = useUIStore();

  const [currentStep, setCurrentStep] = useState('analysis'); // 'analysis', 'enhancements', 'bullets', 'preview'
  const [currentScore, setCurrentScore] = useState(67);
  const [targetScore, setTargetScore] = useState(94);
  const [selectedSection, setSelectedSection] = useState(null);
  const [currentBulletIndex, setCurrentBulletIndex] = useState(0);
  const [appliedChanges, setAppliedChanges] = useState([]);

  const steps = [
    { id: 'analysis', name: 'Analysis', icon: BarChart3 },
    { id: 'enhancements', name: 'Enhance', icon: Sparkles },
    { id: 'bullets', name: 'Bullets', icon: Edit3 },
    { id: 'preview', name: 'Preview', icon: Eye }
  ];

  const mockEnhancements = [
    {
      id: 'add-skills',
      title: 'Add Skills Section',
      description: 'Add comprehensive skills section with job-relevant technologies',
      category: 'high',
      impact: 15,
      available: true,
      proOnly: false,
      previewText: 'Technical Skills: React, Node.js, Python, AWS, Docker...',
      keywords: ['React', 'Node.js', 'Python', 'AWS']
    },
    {
      id: 'enhance-summary',
      title: 'Enhance Professional Summary',
      description: 'Rewrite summary with stronger language and keywords',
      category: 'high',
      impact: 12,
      available: true,
      proOnly: false,
      previewText: 'Senior software engineer with 5+ years building scalable applications...',
      keywords: ['Senior', 'scalable', 'applications']
    },
    {
      id: 'bullet-enhancement',
      title: 'Bullet-by-Bullet Control',
      description: 'Fine-tune each experience bullet individually',
      category: 'advanced',
      impact: 20,
      available: false,
      proOnly: true,
      keywords: ['metrics', 'quantified', 'impact']
    }
  ];

  const mockExperienceSection = {
    jobTitle: 'Software Engineer at TechCorp',
    bullets: [
      { original: 'Developed web applications for clients', enhanced: null },
      { original: 'Worked with team on various projects', enhanced: null },
      { original: 'Maintained existing codebase', enhanced: null }
    ]
  };

  const handleStepChange = (step) => {
    setCurrentStep(step);
    updateMobileUI({ activeStep: step });
  };

  const handleEnhancementToggle = (enhancementId) => {
    const enhancement = mockEnhancements.find(e => e.id === enhancementId);
    if (enhancement) {
      setAppliedChanges(prev => [...prev, {
        id: enhancementId,
        title: enhancement.title,
        impact: enhancement.impact
      }]);
      setCurrentScore(prev => prev + enhancement.impact);
      onEnhancementApply?.(enhancementId);
    }
  };

  const handleBulletEnhancement = (bulletIndex, level) => {
    console.log('Enhancing bullet', bulletIndex, 'with level', level);
    // Implementation would apply the enhancement
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Step Navigation */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = currentStep === step.id;
          const isCompleted = steps.findIndex(s => s.id === currentStep) > index;

          return (
            <button
              key={step.id}
              onClick={() => handleStepChange(step.id)}
              className={`
                flex-1 flex flex-col items-center gap-1 py-2 px-1 rounded-md transition-all
                ${isActive
                  ? 'bg-white text-blue-600 shadow-sm'
                  : isCompleted
                  ? 'text-green-600 hover:bg-white'
                  : 'text-gray-600 hover:bg-white'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{step.name}</span>
            </button>
          );
        })}
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait">
        {currentStep === 'analysis' && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Resume Analysis
              </h2>
              <p className="text-gray-600">
                Detailed breakdown of your resume's ATS performance
              </p>
            </div>

            <MobileResumeAnalysisDashboard
              resumeData={resumeData}
              jobData={jobData}
              currentScore={currentScore}
              potentialScore={targetScore}
              sectionScores={{
                contact: 100,
                summary: 45,
                experience: 78,
                skills: 0,
                education: 65
              }}
              onSectionSelect={setSelectedSection}
            />

            <Button
              onClick={() => handleStepChange('enhancements')}
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white mt-6"
            >
              Start Enhancing
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        )}

        {currentStep === 'enhancements' && (
          <motion.div
            key="enhancements"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Enhancement Options
              </h2>
              <p className="text-gray-600">
                Select improvements to boost your ATS score
              </p>
            </div>

            <MobileEnhancementOptions
              enhancements={mockEnhancements}
              onEnhancementToggle={handleEnhancementToggle}
              onEnhancementPreview={(id) => console.log('Preview:', id)}
              isProUser={isProUser}
              onUpgradeClick={onUpgradeClick}
            />

            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => handleStepChange('analysis')}
                className="flex-1"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={() => handleStepChange('bullets')}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                Fine-tune Bullets
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'bullets' && (
          <motion.div
            key="bullets"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Bullet Enhancement
              </h2>
              <p className="text-gray-600">
                Fine-tune each experience bullet for maximum impact
              </p>
            </div>

            {isProUser ? (
              <MobileBulletEnhancementInterface
                experienceSection={mockExperienceSection}
                currentBulletIndex={currentBulletIndex}
                onBulletChange={setCurrentBulletIndex}
                onEnhancementApply={handleBulletEnhancement}
                isProUser={isProUser}
                onUpgradeClick={onUpgradeClick}
              />
            ) : (
              <div className="text-center py-8">
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-dashed border-purple-200">
                  <Crown className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-purple-900 mb-2">
                    Pro Feature: Bullet-by-Bullet Control
                  </h3>
                  <p className="text-purple-700 mb-4">
                    Upgrade to Pro for granular control over each experience bullet
                  </p>
                  <Button
                    onClick={onUpgradeClick}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                  >
                    <Crown className="w-4 h-4 mr-2" />
                    Upgrade to Pro
                  </Button>
                </div>
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => handleStepChange('enhancements')}
                className="flex-1"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={() => handleStepChange('preview')}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white"
              >
                Preview Results
                <Eye className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {currentStep === 'preview' && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Enhancement Preview
              </h2>
              <p className="text-gray-600">
                Review your improvements and analytics
              </p>
            </div>

            <MobileAnalyticsDisplay
              currentScore={67}
              targetScore={currentScore}
              appliedChanges={appliedChanges}
              keywordAnalysis={{
                added: ['React', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes']
              }}
              transformationMetrics={{
                contentEnhanced: 4,
                metricsAdded: 8,
                estimatedInterviewRateImprovement: 45
              }}
            />

            <div className="flex flex-col gap-3 mt-6">
              <Button
                className="w-full h-12 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
              >
                <Download className="w-5 h-5 mr-2" />
                Download Enhanced Resume
              </Button>
              
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => handleStepChange('bullets')}
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Make Changes
                </Button>
                <Button
                  variant="outline"
                  onClick={onBackToModeSelection}
                  className="flex-1"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  New Job
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default MobilePrecisionModeInterface;