/**
 * ModeSelectionInterface Component
 * Implements the "Control vs Speed" design strategy with tier-based features
 * Provides side-by-side comparison cards for Batch vs Precision modes
 * Enhanced with comprehensive screen reader support and ARIA labels
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  Settings,
  Clock,
  Target,
  CheckCircle,
  ArrowRight,
  Crown,
  Star,
  TrendingUp,
  BarChart3,
  Sparkles
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt, FeatureLockedPrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, hoverLift, scaleIn } from '../lib/motion';
import { useScreenReaderAnnouncement, useAriaLiveRegion } from '../lib/accessibility';

/**
 * ModeCard Component
 * Individual mode selection card with tier-based features
 */
function ModeCard({
  mode,
  title,
  subtitle,
  description,
  icon: Icon,
  features,
  estimatedTime,
  useCase,
  available,
  proOnly,
  recommended,
  onSelect,
  onUpgradeClick,
  isSelected,
  tier,
  className = '',
  announce
}) {
  const isProUser = tier === 'pro';
  const canAccess = available && (!proOnly || isProUser);

  const cardVariants = {
    ...hoverLift,
    selected: {
      scale: 1.02,
      boxShadow: proOnly
        ? '0 8px 25px rgba(147, 51, 234, 0.25)'
        : '0 8px 25px rgba(59, 130, 246, 0.25)',
      borderColor: proOnly ? '#9333ea' : '#3b82f6',
      transition: { duration: 0.3 }
    }
  };

  const cardClassName = `
    h-full cursor-pointer transition-all duration-300 border-2
    ${canAccess ? 'hover:border-opacity-60' : 'opacity-60 cursor-not-allowed'}
    ${isSelected
      ? (proOnly ? 'border-purple-500 bg-purple-50' : 'border-blue-500 bg-blue-50')
      : 'border-gray-200 hover:border-gray-300'}
    ${!canAccess && proOnly ? 'border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50' : ''}
  `;

  const iconClassName = `
    p-3 rounded-xl transition-colors
    ${isSelected
      ? (proOnly ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600')
      : 'bg-gray-100 text-gray-600'}
  `;

  const titleClassName = isSelected
    ? (proOnly ? 'text-purple-900' : 'text-blue-900')
    : 'text-gray-900';

  const checkIconClassName = `
    w-4 h-4 flex-shrink-0
    ${canAccess
      ? (proOnly ? 'text-purple-500' : 'text-blue-500')
      : 'text-gray-400'}
  `;

  const buttonClassName = `w-full transition-all duration-300 text-white shadow-lg hover:shadow-xl ${proOnly
    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
    : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700'
    }`;

  const handleSelect = () => {
    if (canAccess) {
      onSelect(mode);
      announce(`${title} mode selected. ${description}`, 'assertive');
    } else if (proOnly && !isProUser) {
      announce(`${title} mode requires Pro subscription. Click to upgrade.`, 'polite');
    }
  };

  const cardId = `mode-card-${mode}`;
  const descriptionId = `mode-description-${mode}`;
  const featuresId = `mode-features-${mode}`;

  return (
    <motion.div
      variants={cardVariants}
      initial="rest"
      whileHover={canAccess ? "hover" : "rest"}
      animate={isSelected ? "selected" : "rest"}
      className={`relative ${className}`}
    >
      <EnhancedCard
        id={cardId}
        className={cardClassName}
        onClick={handleSelect}
        role="button"
        tabIndex={0}
        aria-pressed={isSelected}
        aria-disabled={!canAccess}
        aria-labelledby={`${cardId}-title`}
        aria-describedby={`${descriptionId} ${featuresId}`}
        data-mode={mode}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleSelect();
          }
        }}
      >
        {/* Pro Badge */}
        {proOnly && (
          <div className="absolute -top-2 -right-2 z-10">
            <TierBadge
              tier="pro"
              size="sm"
              variant="solid"
              animated={true}
              aria-label="Pro subscription required"
            />
          </div>
        )}

        {/* Recommended Badge */}
        {recommended && canAccess && (
          <div className="absolute -top-2 -left-2 z-10">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
            >
              <div
                className="bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg"
                aria-label="Recommended mode for your current selection"
              >
                <Star className="w-3 h-3 inline mr-1" aria-hidden="true" />
                Recommended
              </div>
            </motion.div>
          )}
        )}

            <EnhancedCardHeader>
              <div className="flex items-center gap-3">
                <div className={iconClassName} aria-hidden="true">
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <EnhancedCardTitle
                    id={`${cardId}-title`}
                    size="lg"
                    className={titleClassName}
                  >
                    {title}
                  </EnhancedCardTitle>
                  <EnhancedCardDescription className="text-base font-medium">
                    {subtitle}
                  </EnhancedCardDescription>
                </div>
              </div>
            </EnhancedCardHeader>

            <EnhancedCardContent>
              <p
                id={descriptionId}
                className="text-gray-600 mb-4 leading-relaxed"
              >
                {description}
              </p>

              {/* Time and Use Case */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-500" aria-hidden="true" />
                  <span className="text-gray-600">
                    <span className="sr-only">Estimated processing time: </span>
                    <span className="font-medium">{estimatedTime}</span>
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Target className="w-4 h-4 text-gray-500" aria-hidden="true" />
                  <span className="text-gray-600 font-medium">
                    <span className="sr-only">Best for: </span>
                    {useCase}
                  </span>
                </div>
              </div>

              {/* Features List */}
              <motion.div
                id={featuresId}
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="space-y-2"
                role="list"
                aria-label={`${title} mode features`}
              >
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    variants={staggerItem}
                    className="flex items-center gap-2 text-sm"
                    role="listitem"
                  >
                    <CheckCircle
                      className={checkIconClassName}
                      aria-hidden="true"
                    />
                    <span className={canAccess ? 'text-gray-700' : 'text-gray-500'}>
                      {feature}
                    </span>
                  </motion.div>
                ))}
              </motion.div>
            </EnhancedCardContent>

            <EnhancedCardFooter className="mt-auto">
              {canAccess ? (
                <Button
                  className={buttonClassName}
                  aria-describedby={isSelected ? `${cardId}-selected` : undefined}
                  data-action={isSelected ? 'selected' : 'select-mode'}
                >
                  {isSelected ? 'Selected' : `Choose ${title}`}
                  <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                  {isSelected && (
                    <span id={`${cardId}-selected`} className="sr-only">
                      Currently selected mode
                    </span>
                  )}
                </Button>
              ) : (
                <div className="w-full space-y-3">
                  {/* Feature Preview for Locked Mode */}
                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="text-center space-y-2">
                      <div className="flex items-center justify-center gap-2">
                        <Crown className="w-4 h-4 text-purple-600" />
                        <span className="text-sm font-medium text-purple-700">Pro Feature</span>
                      </div>
                      <p className="text-xs text-gray-600">
                        Unlock {title.toLowerCase()} for advanced control and better results
                      </p>
                    </div>
                  </div>

                  <FeatureLockedPrompt
                    featureName={title}
                    onUpgradeClick={onUpgradeClick}
                  />
                </div>
              )}
            </EnhancedCardFooter>
          </EnhancedCard>
    </motion.div>
  );
}

/**
 * ModeComparisonTable Component
 * Detailed feature comparison between modes
 */
function ModeComparisonTable({ tier }) {
  const isProUser = tier === 'pro';

  const features = [
    {
      category: 'Processing',
      items: [
        { name: 'Jobs per session', batch: '1 (Free) / 25 (Pro)', precision: '1 job focus' },
        { name: 'Processing time', batch: '2-3 minutes', precision: '5-10 minutes' },
        { name: 'User involvement', batch: 'Minimal', precision: 'High control' }
      ]
    },
    {
      category: 'Enhancement Control',
      items: [
        { name: 'Enhancement level', batch: 'Global settings', precision: 'Bullet-by-bullet' },
        { name: 'Preview changes', batch: 'Final result only', precision: 'Real-time preview' },
        { name: 'Custom editing', batch: 'Not available', precision: 'Full editing control' }
      ]
    },
    {
      category: 'Analytics & Insights',
      items: [
        { name: 'ATS score tracking', batch: 'Basic scoring', precision: 'Real-time updates' },
        { name: 'Keyword analysis', batch: 'Summary report', precision: 'Detailed breakdown' },
        { name: 'Impact scoring', batch: 'Overall impact', precision: 'Per-change impact' }
      ]
    }
  ];

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="mt-8"
    >
      <EnhancedCard>
        <EnhancedCardHeader>
          <EnhancedCardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Feature Comparison
          </EnhancedCardTitle>
          <EnhancedCardDescription>
            Detailed comparison of Batch Mode vs Precision Mode capabilities
          </EnhancedCardDescription>
        </EnhancedCardHeader>
        <EnhancedCardContent>
          <div className="space-y-6">
            {features.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" />
                  {category.category}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="font-medium text-gray-700 text-sm">Feature</div>
                  <div className="font-medium text-blue-700 text-sm">Batch Mode</div>
                  <div className="font-medium text-purple-700 text-sm">Precision Mode</div>

                  {category.items.map((item, itemIndex) => (
                    <React.Fragment key={itemIndex}>
                      <div className="text-sm text-gray-600 py-2 border-t border-gray-100">
                        {item.name}
                      </div>
                      <div className="text-sm text-gray-700 py-2 border-t border-gray-100">
                        {item.batch}
                      </div>
                      <div className={`text-sm py-2 border-t border-gray-100 ${!isProUser && item.name.includes('Custom') ? 'text-gray-400' : 'text-gray-700'
                        }`}>
                        {item.precision}
                        {!isProUser && item.name.includes('Custom') && (
                          <TierBadge tier="pro" size="sm" className="ml-2" />
                        )}
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * ProUserWorkflowSuggestions Component
 * Provides hybrid workflow recommendations for pro users
 */
function ProUserWorkflowSuggestions({ jobCount, selectedMode, onModeSelect }) {
  const getWorkflowSuggestion = () => {
    if (jobCount === 1) {
      return {
        title: 'Single Job Application',
        recommendation: 'Precision Mode',
        reason: 'Perfect for detailed customization of important applications',
        workflow: [
          'Use Precision Mode for granular control',
          'Review each enhancement individually',
          'Optimize for maximum ATS score',
          'Export with detailed analytics'
        ],
        alternative: {
          mode: 'Batch Mode',
          reason: 'If you need quick results for this application'
        }
      };
    } else if (jobCount <= 5) {
      return {
        title: 'Small Batch Processing',
        recommendation: 'Hybrid Approach',
        reason: 'Combine speed and precision for optimal results',
        workflow: [
          'Start with Batch Mode for all jobs',
          'Review batch results and rankings',
          'Use Precision Mode for top 2-3 jobs',
          'Fine-tune the most promising applications'
        ],
        alternative: {
          mode: 'Batch Mode Only',
          reason: 'If time is limited and you need quick results'
        }
      };
    } else {
      return {
        title: 'Large Batch Processing',
        recommendation: 'Batch Mode',
        reason: 'Efficiently process multiple applications with consistent quality',
        workflow: [
          'Use Batch Mode with Balanced enhancement',
          'Review aggregate analytics',
          'Identify top-performing applications',
          'Consider Precision Mode for final candidates'
        ],
        alternative: {
          mode: 'Precision Mode',
          reason: 'For the most important 1-2 applications after batch processing'
        }
      };
    }
  };

  const suggestion = getWorkflowSuggestion();

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
    >
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <TrendingUp className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{suggestion.title}</h3>
            <p className="text-sm text-gray-600">Optimized workflow for {jobCount} job{jobCount > 1 ? 's' : ''}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-blue-100">
          <div className="flex items-center gap-2 mb-2">
            <Star className="w-4 h-4 text-yellow-500" />
            <span className="font-medium text-gray-900">Recommended: {suggestion.recommendation}</span>
          </div>
          <p className="text-sm text-gray-600 mb-3">{suggestion.reason}</p>

          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Suggested Workflow:</h4>
            <ol className="space-y-1">
              {suggestion.workflow.map((step, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Settings className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Alternative: {suggestion.alternative.mode}</span>
          </div>
          <p className="text-xs text-gray-600">{suggestion.alternative.reason}</p>
        </div>

        {suggestion.recommendation.includes('Hybrid') && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onModeSelect('batch')}
              className="flex-1 border-blue-300 text-blue-700 hover:bg-blue-50"
            >
              Start with Batch
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onModeSelect('precision')}
              className="flex-1 border-purple-300 text-purple-700 hover:bg-purple-50"
            >
              Go to Precision
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

/**
 * ProUserAdvancedFeatures Component
 * Highlights advanced features available to pro users
 */
function ProUserAdvancedFeatures() {
  const advancedFeatures = [
    {
      category: 'Processing Power',
      icon: Zap,
      features: [
        'Process up to 25 jobs simultaneously',
        'Priority processing queue',
        'Advanced batch analytics',
        'Bulk export options'
      ]
    },
    {
      category: 'Precision Control',
      icon: Target,
      features: [
        'Bullet-by-bullet enhancement',
        'Real-time ATS score updates',
        'Custom enhancement editing',
        'Before/after comparisons'
      ]
    },
    {
      category: 'Analytics & Insights',
      icon: BarChart3,
      features: [
        'Detailed transformation metrics',
        'Keyword analysis dashboard',
        'Interview rate predictions',
        'Exportable analytics reports'
      ]
    }
  ];

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200"
    >
      <div className="space-y-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Crown className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-purple-900">Pro Features Active</h3>
          </div>
          <p className="text-sm text-purple-700">You have access to all advanced capabilities</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {advancedFeatures.map((category, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + (index * 0.1) }}
              className="bg-white rounded-lg p-4 border border-purple-100"
            >
              <div className="flex items-center gap-2 mb-3">
                <category.icon className="w-4 h-4 text-purple-600" />
                <h4 className="font-medium text-gray-900">{category.category}</h4>
              </div>
              <ul className="space-y-1">
                {category.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center gap-2 text-xs text-gray-600">
                    <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

/**
 * ModeProgressTracker Component
 * Shows progress and allows switching between modes without losing progress
 */
function ModeProgressTracker({
  currentMode,
  batchProgress,
  precisionProgress,
  onModeSwitch,
  canSwitchModes = true
}) {
  const progressData = {
    batch: {
      label: 'Batch Mode Progress',
      progress: batchProgress || 0,
      status: batchProgress > 0 ? 'In Progress' : 'Not Started',
      icon: Zap
    },
    precision: {
      label: 'Precision Mode Progress',
      progress: precisionProgress || 0,
      status: precisionProgress > 0 ? 'In Progress' : 'Not Started',
      icon: Settings
    }
  };

  if (!batchProgress && !precisionProgress) return null;

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm"
    >
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-gray-900 flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Session Progress
        </h3>

        <div className="space-y-3">
          {Object.entries(progressData).map(([mode, data]) => {
            const Icon = data.icon;
            const isActive = currentMode === mode;
            const hasProgress = data.progress > 0;

            return (
              <div
                key={mode}
                className={`
                  flex items-center justify-between p-3 rounded-lg border transition-all
                  ${isActive ? 'border-blue-300 bg-blue-50' : 'border-gray-200'}
                `}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{data.label}</div>
                    <div className="text-xs text-gray-500">{data.status}</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {hasProgress && (
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${data.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{data.progress}%</span>
                    </div>
                  )}

                  {canSwitchModes && !isActive && hasProgress && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onModeSwitch(mode)}
                      className="text-xs"
                    >
                      Resume
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

/**
 * FreeUserValueDemo Component
 * Shows potential score improvements and pro features preview
 */
function FreeUserValueDemo({ onUpgradeClick }) {
  const demoMetrics = {
    currentScore: 67,
    proScore: 94,
    improvement: 27,
    features: [
      { name: 'Advanced keyword optimization', impact: '+12 points' },
      { name: 'Industry-specific enhancements', impact: '+8 points' },
      { name: 'Quantified achievements', impact: '+7 points' }
    ]
  };

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-dashed border-purple-200"
    >
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-purple-900">
            See What Pro Can Do
          </h3>
        </div>

        {/* Score Improvement Preview */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600 mb-1">67</div>
            <div className="text-sm text-gray-500">Current Score</div>
          </div>
          <div className="flex items-center justify-center">
            <ArrowRight className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">94</div>
            <div className="text-sm text-purple-700">Pro Score</div>
          </div>
        </div>

        {/* Feature Impact Breakdown */}
        <div className="space-y-3 mb-6">
          {demoMetrics.features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + (index * 0.1) }}
              className="flex items-center justify-between bg-white rounded-lg p-3 shadow-sm"
            >
              <span className="text-sm text-gray-700">{feature.name}</span>
              <span className="text-sm font-semibold text-green-600">{feature.impact}</span>
            </motion.div>
          ))}
        </div>

        <Button
          onClick={onUpgradeClick}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl transition-all"
        >
          <Crown className="w-4 h-4 mr-2" />
          Unlock Pro Features
        </Button>

        <p className="text-xs text-purple-600">
          +{demoMetrics.improvement} point improvement potential
        </p>
      </div>
    </motion.div>
  );
}

/**
 * UpgradeValueProposition Component
 * Contextual upgrade messaging based on user behavior
 */
function UpgradeValueProposition({
  context = 'general',
  weeklyUsage,
  weeklyLimit,
  jobCount,
  onUpgradeClick
}) {
  const getContextualMessage = () => {
    if (weeklyUsage >= weeklyLimit) {
      return {
        title: 'Weekly Limit Reached',
        message: 'You\'ve used all your free sessions this week. Upgrade for unlimited access.',
        urgency: 'high',
        benefits: ['Unlimited weekly sessions', 'No waiting for resets', 'Process anytime']
      };
    }

    if (weeklyUsage >= weeklyLimit - 1) {
      return {
        title: 'Almost at Your Limit',
        message: `Only ${weeklyLimit - weeklyUsage} session remaining this week.`,
        urgency: 'medium',
        benefits: ['Never worry about limits', 'Unlimited processing', 'Advanced features']
      };
    }

    if (jobCount > 1) {
      return {
        title: 'Batch Processing Available',
        message: `Process all ${jobCount} jobs at once with Pro batch mode.`,
        urgency: 'medium',
        benefits: ['Process up to 25 jobs', 'Save hours of time', 'Bulk optimization']
      };
    }

    return {
      title: 'Unlock Advanced Features',
      message: 'Get precision control and unlimited processing with Pro.',
      urgency: 'low',
      benefits: ['Bullet-by-bullet control', 'Real-time previews', 'Advanced analytics']
    };
  };

  const { title, message, urgency, benefits } = getContextualMessage();

  const urgencyStyles = {
    high: 'border-red-300 bg-red-50 text-red-800',
    medium: 'border-amber-300 bg-amber-50 text-amber-800',
    low: 'border-purple-300 bg-purple-50 text-purple-800'
  };

  const buttonStyles = {
    high: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800',
    medium: 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700',
    low: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
  };

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={`rounded-xl p-6 border-2 border-dashed ${urgencyStyles[urgency]}`}
    >
      <div className="text-center space-y-4">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm opacity-90">{message}</p>
        </div>

        <div className="space-y-2">
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + (index * 0.1) }}
              className="flex items-center gap-2 text-sm"
            >
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>{benefit}</span>
            </motion.div>
          ))}
        </div>

        <Button
          onClick={onUpgradeClick}
          className={`w-full ${buttonStyles[urgency]} text-white shadow-lg hover:shadow-xl transition-all`}
        >
          <Zap className="w-4 h-4 mr-2" />
          Upgrade Now
        </Button>
      </div>
    </motion.div>
  );
}

/**
 * Main ModeSelectionInterface Component
 */
export function ModeSelectionInterface({
  resumeData,
  jobUrls = [],
  onModeSelect,
  onUpgradeClick,
  estimatedProcessingTime = { batch: '2-3 min', precision: '5-10 min' },
  className = ''
}) {
  const { user, tier, weeklyUsage, weeklyLimit } = useUserStore();
  const { selectedMode, setSelectedMode } = useProcessingStore();
  const { updateMobileUI } = useUIStore();

  const [showComparison, setShowComparison] = useState(false);
  const [selectedModeLocal, setSelectedModeLocal] = useState(selectedMode);
  const [showValueDemo, setShowValueDemo] = useState(false);

  // Screen reader support
  const announce = useScreenReaderAnnouncement();
  const liveRegionAnnounce = useAriaLiveRegion('mode-selection-announcements');

  const isProUser = tier === 'pro';
  const jobCount = jobUrls.length;
  const hasExceededLimit = weeklyUsage >= weeklyLimit;
  const isApproachingLimit = weeklyUsage >= weeklyLimit - 1;

  // Mode configurations based on user tier
  const getModeConfig = () => {
    if (isProUser) {
      return {
        batch: {
          title: 'Batch Mode',
          subtitle: 'Fast & Reliable',
          description: 'Process multiple jobs quickly with global enhancement settings. Perfect for applying to many positions efficiently.',
          icon: Zap,
          features: [
            `Process up to 25 jobs at once`,
            'Global enhancement settings',
            'Live processing visualization',
            'Batch results overview',
            'Advanced analytics dashboard'
          ],
          estimatedTime: estimatedProcessingTime.batch,
          useCase: 'Multiple applications',
          available: true,
          proOnly: false,
          recommended: jobCount > 1
        },
        precision: {
          title: 'Precision Mode',
          subtitle: 'Perfect & Controlled',
          description: 'Granular control over every enhancement with real-time impact preview. Ideal for important applications.',
          icon: Settings,
          features: [
            'Bullet-by-bullet enhancement control',
            'Real-time ATS score updates',
            'Before/after comparisons',
            'Custom enhancement editing',
            'Detailed transformation analytics'
          ],
          estimatedTime: estimatedProcessingTime.precision,
          useCase: 'Important applications',
          available: true,
          proOnly: true,
          recommended: jobCount === 1
        }
      };
    } else {
      return {
        batch: {
          title: 'Quick Mode',
          subtitle: 'Fast & Reliable',
          description: 'Smart optimization with automatic enhancements. Get your resume tailored quickly with minimal decisions.',
          icon: Zap,
          features: [
            'Process 1 job quickly',
            'Smart auto-enhancements',
            'Basic ATS optimization',
            'Standard formatting',
            'Quick results'
          ],
          estimatedTime: estimatedProcessingTime.batch,
          useCase: 'Quick applications',
          available: true,
          proOnly: false,
          recommended: true
        },
        precision: {
          title: 'Precision Mode',
          subtitle: 'Pro Feature',
          description: 'Unlock granular control with bullet-by-bullet enhancement, real-time previews, and advanced analytics.',
          icon: Crown,
          features: [
            'Bullet-by-bullet control',
            'Real-time impact preview',
            'Advanced enhancement options',
            'Detailed analytics dashboard',
            'Custom editing capabilities'
          ],
          estimatedTime: estimatedProcessingTime.precision,
          useCase: 'Perfect applications',
          available: false,
          proOnly: true,
          recommended: false
        }
      };
    }
  };

  const modeConfig = getModeConfig();

  const handleModeSelect = (mode) => {
    setSelectedModeLocal(mode);
    setSelectedMode(mode);

    // Update mobile UI
    updateMobileUI({ activeTab: `${mode}-mode` });

    // Call parent callback
    onModeSelect?.(mode);
  };

  const handleUpgradeClick = () => {
    // Handle upgrade flow
    console.log('Upgrade clicked from mode selection');
    onUpgradeClick?.();
  };

  const handleShowValueDemo = () => {
    setShowValueDemo(true);
  };

  return (
    <section
      role="main"
      aria-labelledby="mode-selection-heading"
      className={`space-y-6 ${className}`}
    >
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Screen reader live region for announcements */}
        <div
          id="mode-selection-announcements"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        />

        {/* Header Section */}
        <motion.div variants={staggerItem} className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Sparkles
              className="w-6 h-6 text-purple-600"
              aria-hidden="true"
            />
            <h2
              id="mode-selection-heading"
              className="text-2xl font-bold text-gray-900"
            >
              Choose Your Enhancement Mode
            </h2>
          </div>
          <p
            className="text-gray-600 max-w-2xl mx-auto leading-relaxed"
            id="mode-selection-description"
          >
            Select the approach that matches your intent and time availability.
            {isProUser
              ? ' You have access to both modes with full features.'
              : ' Upgrade to Pro for advanced precision control and unlimited processing.'
            }
          </p>

          {/* Usage Status for Free Users */}
          {!isProUser && (
            <motion.div variants={fadeInUp} className="max-w-md mx-auto">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-blue-700">Weekly usage:</span>
                  <span className="font-medium text-blue-900">{weeklyUsage}/{weeklyLimit}</span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-cyan-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min((weeklyUsage / weeklyLimit) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Mode Selection Cards */}
        <motion.div
          variants={staggerItem}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto"
          role="group"
          aria-labelledby="mode-selection-heading"
          aria-describedby="mode-selection-description"
        >
          <ModeCard
            mode="batch"
            {...modeConfig.batch}
            onSelect={handleModeSelect}
            onUpgradeClick={handleUpgradeClick}
            isSelected={selectedModeLocal === 'batch'}
            tier={tier}
            announce={liveRegionAnnounce}
          />
          <ModeCard
            mode="precision"
            {...modeConfig.precision}
            onSelect={handleModeSelect}
            onUpgradeClick={handleUpgradeClick}
            isSelected={selectedModeLocal === 'precision'}
            tier={tier}
            announce={liveRegionAnnounce}
          />
        </motion.div>

        {/* Pro User Experience Enhancement */}
        {isProUser ? (
          <motion.div variants={staggerItem} className="space-y-6">
            {/* Workflow Suggestions */}
            <div className="max-w-4xl mx-auto">
              <ProUserWorkflowSuggestions
                jobCount={jobCount}
                selectedMode={selectedModeLocal}
                onModeSelect={handleModeSelect}
              />
            </div>

            {/* Advanced Features Showcase */}
            <div className="max-w-6xl mx-auto">
              <ProUserAdvancedFeatures />
            </div>

            {/* Progress Tracker (if there's existing progress) */}
            <div className="max-w-2xl mx-auto">
              <ModeProgressTracker
                currentMode={selectedModeLocal}
                batchProgress={0} // This would come from actual progress state
                precisionProgress={0} // This would come from actual progress state
                onModeSwitch={handleModeSelect}
                canSwitchModes={true}
              />
            </div>
          </motion.div>
        ) : (
          /* Free User Experience Enhancement */
          <motion.div variants={staggerItem} className="space-y-6">
            {/* Contextual Upgrade Messaging */}
            <div className="max-w-2xl mx-auto">
              <UpgradeValueProposition
                context={hasExceededLimit ? 'limit_reached' : isApproachingLimit ? 'approaching_limit' : jobCount > 1 ? 'batch_processing' : 'general'}
                weeklyUsage={weeklyUsage}
                weeklyLimit={weeklyLimit}
                jobCount={jobCount}
                onUpgradeClick={handleUpgradeClick}
              />
            </div>

            {/* Value Demonstration */}
            <div className="max-w-md mx-auto">
              <AnimatePresence>
                {showValueDemo ? (
                  <FreeUserValueDemo onUpgradeClick={handleUpgradeClick} />
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center"
                  >
                    <Button
                      variant="outline"
                      onClick={handleShowValueDemo}
                      className="border-purple-300 text-purple-700 hover:bg-purple-50"
                    >
                      <TrendingUp className="w-4 h-4 mr-2" />
                      See Pro Score Preview
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* Feature Comparison Toggle */}
        <motion.div variants={staggerItem} className="text-center">
          <Button
            variant="outline"
            onClick={() => setShowComparison(!showComparison)}
            className="text-gray-600 hover:text-gray-900"
          >
            {showComparison ? 'Hide' : 'Show'} Detailed Comparison
            <TrendingUp className="w-4 h-4 ml-2" />
          </Button>
        </motion.div>

        {/* Feature Comparison Table */}
        <AnimatePresence>
          {showComparison && (
            <ModeComparisonTable tier={tier} />
          )}
        </AnimatePresence>

        {/* Continue Button */}
        {selectedModeLocal && (
          <motion.div
            variants={scaleIn}
            initial="hidden"
            animate="visible"
            className="text-center pt-4"
          >
            <Button
              size="lg"
              className={`px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all text-white ${selectedModeLocal === 'precision' && isProUser
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700'
                }`}
              onClick={() => {
                // Proceed to the selected mode interface
                console.log(`Proceeding with ${selectedModeLocal} mode`);
              }}
            >
              Continue with {modeConfig[selectedModeLocal].title}
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        )}
      </motion.div>
      );
}

      export default ModeSelectionInterface;