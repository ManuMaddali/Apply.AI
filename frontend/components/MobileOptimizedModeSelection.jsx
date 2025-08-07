/**
 * MobileOptimizedModeSelection Component
 * Mobile-first responsive design for mode selection with touch-friendly interactions
 * Implements swipe gestures, condensed layouts, and mobile-specific upgrade flows
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, PanInfo } from 'framer-motion';
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
  Sparkles,
  ChevronLeft,
  ChevronRight,
  X,
  Info,
  Smartphone,
  Tablet,
  Monitor
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, slideInFromRight, slideInFromLeft } from '../lib/motion';

/**
 * MobileModeCard Component
 * Touch-optimized mode selection card for mobile devices
 */
function MobileModeCard({
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
  isActive = false,
  className = ''
}) {
  const isProUser = tier === 'pro';
  const canAccess = available && (!proOnly || isProUser);

  const cardVariants = {
    inactive: {
      scale: 0.95,
      opacity: 0.7,
      x: 0
    },
    active: {
      scale: 1,
      opacity: 1,
      x: 0,
      transition: { type: 'spring', stiffness: 300, damping: 30 }
    },
    selected: {
      scale: 1.02,
      opacity: 1,
      x: 0,
      boxShadow: proOnly
        ? '0 12px 30px rgba(147, 51, 234, 0.3)'
        : '0 12px 30px rgba(59, 130, 246, 0.3)',
      transition: { type: 'spring', stiffness: 300, damping: 30 }
    }
  };

  const getCardState = () => {
    if (isSelected) return 'selected';
    if (isActive) return 'active';
    return 'inactive';
  };

  return (
    <motion.div
      variants={cardVariants}
      animate={getCardState()}
      className={`w-full max-w-sm mx-auto ${className}`}
      style={{ minHeight: '400px' }}
    >
      <EnhancedCard
        className={`
          h-full cursor-pointer transition-all duration-300 border-2 relative
          ${canAccess ? 'active:scale-95' : 'opacity-60 cursor-not-allowed'}
          ${isSelected
            ? (proOnly ? 'border-purple-500 bg-purple-50' : 'border-blue-500 bg-blue-50')
            : 'border-gray-200'}
          ${!canAccess && proOnly ? 'border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50' : ''}
        `}
        onClick={canAccess ? () => onSelect(mode) : undefined}
      >
        {/* Pro Badge */}
        {proOnly && (
          <div className="absolute -top-2 -right-2 z-10">
            <TierBadge
              tier="pro"
              size="sm"
              variant="solid"
              animated={true}
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
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                <Star className="w-3 h-3 inline mr-1" />
                Best Choice
              </div>
            </motion.div>
          )}
        )}

        <EnhancedCardHeader className="text-center pb-4">
          <div className="flex flex-col items-center gap-3">
            <div className={`
              p-4 rounded-2xl transition-colors
              ${isSelected
                ? (proOnly ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600')
                : 'bg-gray-100 text-gray-600'}
            `}>
              <Icon className="w-8 h-8" />
            </div>
            <div>
              <EnhancedCardTitle size="xl" className={`
                ${isSelected
                  ? (proOnly ? 'text-purple-900' : 'text-blue-900')
                  : 'text-gray-900'}
              `}>
                {title}
              </EnhancedCardTitle>
              <EnhancedCardDescription className="text-lg font-medium mt-1">
                {subtitle}
              </EnhancedCardDescription>
            </div>
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent className="px-6">
          <p className="text-gray-600 mb-6 leading-relaxed text-center">
            {description}
          </p>

          {/* Time and Use Case - Mobile Optimized */}
          <div className="space-y-3 mb-6">
            <div className="flex items-center justify-center gap-2 bg-gray-50 rounded-lg p-3">
              <Clock className="w-5 h-5 text-gray-500" />
              <span className="text-gray-700 font-medium">{estimatedTime}</span>
            </div>
            <div className="flex items-center justify-center gap-2 bg-gray-50 rounded-lg p-3">
              <Target className="w-5 h-5 text-gray-500" />
              <span className="text-gray-700 font-medium">{useCase}</span>
            </div>
          </div>

          {/* Features List - Condensed for Mobile */}
          <div className="space-y-2">
            {features.slice(0, 3).map((feature, index) => (
              <div
                key={index}
                className="flex items-center gap-3 text-sm bg-white rounded-lg p-2 border border-gray-100"
              >
                <CheckCircle className={`
                  w-4 h-4 flex-shrink-0
                  ${canAccess
                    ? (proOnly ? 'text-purple-500' : 'text-blue-500')
                    : 'text-gray-400'}
                `} />
                <span className={canAccess ? 'text-gray-700' : 'text-gray-500'}>
                  {feature}
                </span>
              </div>
            ))}
            
            {features.length > 3 && (
              <div className="text-center">
                <span className="text-xs text-gray-500">
                  +{features.length - 3} more features
                </span>
              </div>
            )}
          </div>
        </EnhancedCardContent>

        <EnhancedCardFooter className="mt-auto px-6 pb-6">
          {canAccess ? (
            <Button 
              className={`
                w-full h-12 text-base font-semibold transition-all duration-300 text-white shadow-lg active:scale-95
                ${proOnly
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 active:from-purple-700 active:to-pink-700'
                  : 'bg-gradient-to-r from-blue-600 to-cyan-600 active:from-blue-700 active:to-cyan-700'
                }
              `}
            >
              {isSelected ? 'Selected' : `Choose ${title}`}
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          ) : (
            <div className="w-full space-y-3">
              {/* Mobile-Optimized Upgrade Prompt */}
              <div className="bg-white rounded-lg p-4 border-2 border-purple-200 text-center">
                <Crown className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-purple-700 mb-1">Pro Feature</p>
                <p className="text-xs text-gray-600 mb-3">
                  Unlock {title.toLowerCase()} for advanced control
                </p>
                <Button
                  onClick={onUpgradeClick}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white h-10 text-sm font-semibold active:scale-95"
                >
                  Upgrade Now
                </Button>
              </div>
            </div>
          )}
        </EnhancedCardFooter>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * SwipeableModeSelector Component
 * Implements swipe gestures for mode comparison on mobile
 */
function SwipeableModeSelector({
  modes,
  selectedMode,
  onModeSelect,
  onUpgradeClick,
  tier
}) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const x = useMotionValue(0);
  const containerRef = useRef(null);

  const handleDragEnd = (event, info) => {
    setIsDragging(false);
    const threshold = 50;
    
    if (info.offset.x > threshold && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    } else if (info.offset.x < -threshold && currentIndex < modes.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
    
    x.set(0);
  };

  const handleDragStart = () => {
    setIsDragging(true);
  };

  const goToMode = (index) => {
    setCurrentIndex(index);
  };

  return (
    <div className="relative w-full overflow-hidden">
      {/* Swipe Indicator */}
      <div className="flex justify-center mb-4">
        <div className="flex items-center gap-2 bg-gray-100 rounded-full px-4 py-2">
          <ChevronLeft className="w-4 h-4 text-gray-400" />
          <span className="text-xs text-gray-600">Swipe to compare</span>
          <ChevronRight className="w-4 h-4 text-gray-400" />
        </div>
      </div>

      {/* Mode Cards Container */}
      <motion.div
        ref={containerRef}
        className="flex"
        style={{ x }}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.2}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        animate={{ x: -currentIndex * 100 + '%' }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {modes.map((mode, index) => (
          <div key={mode.mode} className="w-full flex-shrink-0 px-4">
            <MobileModeCard
              {...mode}
              onSelect={onModeSelect}
              onUpgradeClick={onUpgradeClick}
              isSelected={selectedMode === mode.mode}
              isActive={index === currentIndex}
              tier={tier}
            />
          </div>
        ))}
      </motion.div>

      {/* Navigation Dots */}
      <div className="flex justify-center mt-6 gap-2">
        {modes.map((_, index) => (
          <button
            key={index}
            onClick={() => goToMode(index)}
            className={`
              w-3 h-3 rounded-full transition-all duration-300 active:scale-90
              ${index === currentIndex
                ? 'bg-blue-500 scale-110'
                : 'bg-gray-300 hover:bg-gray-400'}
            `}
          />
        ))}
      </div>

      {/* Navigation Arrows for Non-Touch Devices */}
      <div className="hidden sm:block">
        {currentIndex > 0 && (
          <button
            onClick={() => goToMode(currentIndex - 1)}
            className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-white rounded-full shadow-lg border border-gray-200 hover:bg-gray-50 active:scale-95"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
        )}
        
        {currentIndex < modes.length - 1 && (
          <button
            onClick={() => goToMode(currentIndex + 1)}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-white rounded-full shadow-lg border border-gray-200 hover:bg-gray-50 active:scale-95"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * MobileFeatureComparison Component
 * Condensed feature comparison optimized for mobile screens
 */
function MobileFeatureComparison({ tier, isVisible, onClose }) {
  const isProUser = tier === 'pro';

  const comparisonData = [
    {
      category: 'Processing',
      features: [
        { name: 'Jobs per session', batch: isProUser ? '25 jobs' : '1 job', precision: '1 job focus' },
        { name: 'Processing time', batch: '2-3 min', precision: '5-10 min' },
        { name: 'Control level', batch: 'Global', precision: 'Granular' }
      ]
    },
    {
      category: 'Features',
      features: [
        { name: 'Enhancement', batch: 'Auto-applied', precision: 'Manual control' },
        { name: 'Preview', batch: 'Final only', precision: 'Real-time' },
        { name: 'Analytics', batch: 'Basic', precision: 'Advanced' }
      ]
    }
  ];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="bg-white rounded-t-2xl sm:rounded-2xl w-full max-w-md max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Feature Comparison</h3>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full active:scale-90"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-6">
              {comparisonData.map((category, categoryIndex) => (
                <div key={categoryIndex}>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" />
                    {category.category}
                  </h4>
                  
                  <div className="space-y-3">
                    {category.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="bg-gray-50 rounded-lg p-3">
                        <div className="font-medium text-gray-800 text-sm mb-2">
                          {feature.name}
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div className="bg-blue-100 rounded-lg p-2 text-center">
                            <div className="text-blue-700 font-medium">Batch</div>
                            <div className="text-blue-600">{feature.batch}</div>
                          </div>
                          <div className="bg-purple-100 rounded-lg p-2 text-center">
                            <div className="text-purple-700 font-medium">Precision</div>
                            <div className="text-purple-600">{feature.precision}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * MobileUpgradeFlow Component
 * Mobile-optimized upgrade flow with payment integration
 */
function MobileUpgradeFlow({ isVisible, onClose, onUpgrade, context = 'mode-selection' }) {
  const [selectedPlan, setSelectedPlan] = useState('monthly');
  const [isProcessing, setIsProcessing] = useState(false);

  const plans = {
    monthly: {
      name: 'Monthly Pro',
      price: '$19',
      period: '/month',
      features: [
        'Unlimited processing',
        'Batch mode (25 jobs)',
        'Precision mode',
        'Advanced analytics',
        'Priority support'
      ],
      popular: false
    },
    yearly: {
      name: 'Yearly Pro',
      price: '$190',
      period: '/year',
      originalPrice: '$228',
      savings: 'Save $38',
      features: [
        'Everything in Monthly',
        '2 months free',
        'Advanced features first',
        'Premium support',
        'Export capabilities'
      ],
      popular: true
    }
  };

  const handleUpgrade = async () => {
    setIsProcessing(true);
    try {
      await onUpgrade(selectedPlan);
    } catch (error) {
      console.error('Upgrade failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center"
          onClick={onClose}
        >
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="bg-white rounded-t-2xl sm:rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Crown className="w-5 h-5 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Upgrade to Pro</h3>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full active:scale-90"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-6">
              {/* Context Message */}
              <div className="text-center">
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-4">
                  <Sparkles className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                  <p className="text-sm text-purple-800">
                    {context === 'mode-selection' 
                      ? 'Unlock Precision Mode and unlimited processing'
                      : 'Get access to all Pro features'}
                  </p>
                </div>
              </div>

              {/* Plan Selection */}
              <div className="space-y-3">
                {Object.entries(plans).map(([planKey, plan]) => (
                  <motion.div
                    key={planKey}
                    whileTap={{ scale: 0.98 }}
                    className={`
                      relative border-2 rounded-xl p-4 cursor-pointer transition-all
                      ${selectedPlan === planKey
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'}
                    `}
                    onClick={() => setSelectedPlan(planKey)}
                  >
                    {plan.popular && (
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                          Most Popular
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{plan.name}</h4>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold text-gray-900">{plan.price}</span>
                          <span className="text-gray-600">{plan.period}</span>
                          {plan.originalPrice && (
                            <span className="text-sm text-gray-500 line-through ml-2">
                              {plan.originalPrice}
                            </span>
                          )}
                        </div>
                        {plan.savings && (
                          <div className="text-sm text-green-600 font-medium">{plan.savings}</div>
                        )}
                      </div>
                      <div className={`
                        w-5 h-5 rounded-full border-2 flex items-center justify-center
                        ${selectedPlan === planKey
                          ? 'border-purple-500 bg-purple-500'
                          : 'border-gray-300'}
                      `}>
                        {selectedPlan === planKey && (
                          <div className="w-2 h-2 bg-white rounded-full" />
                        )}
                      </div>
                    </div>

                    <div className="space-y-1">
                      {plan.features.slice(0, 3).map((feature, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                          {feature}
                        </div>
                      ))}
                      {plan.features.length > 3 && (
                        <div className="text-xs text-gray-500 ml-5">
                          +{plan.features.length - 3} more features
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Upgrade Button */}
              <Button
                onClick={handleUpgrade}
                disabled={isProcessing}
                className="w-full h-12 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold text-base active:scale-95 disabled:opacity-50"
              >
                {isProcessing ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Processing...
                  </div>
                ) : (
                  <>
                    Upgrade to {plans[selectedPlan].name}
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </>
                )}
              </Button>

              {/* Trust Indicators */}
              <div className="text-center space-y-2">
                <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <CheckCircle className="w-3 h-3 text-green-500" />
                    Cancel anytime
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="w-3 h-3 text-green-500" />
                    Secure payment
                  </div>
                </div>
                <p className="text-xs text-gray-500">
                  30-day money-back guarantee
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * DeviceOptimizedLayout Component
 * Adapts layout based on device type and screen size
 */
function DeviceOptimizedLayout({ children, deviceType = 'mobile' }) {
  const layoutClasses = {
    mobile: 'px-4 py-6 space-y-6',
    tablet: 'px-6 py-8 space-y-8',
    desktop: 'px-8 py-10 space-y-10'
  };

  const containerClasses = {
    mobile: 'max-w-sm mx-auto',
    tablet: 'max-w-2xl mx-auto',
    desktop: 'max-w-4xl mx-auto'
  };

  return (
    <div className={`${layoutClasses[deviceType]} ${containerClasses[deviceType]}`}>
      {children}
    </div>
  );
}

/**
 * Main MobileOptimizedModeSelection Component
 */
export function MobileOptimizedModeSelection({
  resumeData,
  jobUrls = [],
  onModeSelect,
  onUpgradeClick,
  estimatedProcessingTime = { batch: '2-3 min', precision: '5-10 min' },
  className = ''
}) {
  const { user, tier, weeklyUsage, weeklyLimit } = useUserStore();
  const { selectedMode, setSelectedMode } = useProcessingStore();
  const { mobileUI, updateMobileUI } = useUIStore();

  const [showComparison, setShowComparison] = useState(false);
  const [showUpgradeFlow, setShowUpgradeFlow] = useState(false);
  const [deviceType, setDeviceType] = useState('mobile');

  const isProUser = tier === 'pro';
  const jobCount = jobUrls.length;

  // Detect device type
  useEffect(() => {
    const updateDeviceType = () => {
      const width = window.innerWidth;
      if (width < 640) setDeviceType('mobile');
      else if (width < 1024) setDeviceType('tablet');
      else setDeviceType('desktop');
    };

    updateDeviceType();
    window.addEventListener('resize', updateDeviceType);
    return () => window.removeEventListener('resize', updateDeviceType);
  }, []);

  // Mode configurations optimized for mobile
  const getMobileModesConfig = () => {
    if (isProUser) {
      return [
        {
          mode: 'batch',
          title: 'Batch Mode',
          subtitle: 'Fast & Reliable',
          description: 'Process multiple jobs quickly with smart automation. Perfect for applying to many positions efficiently.',
          icon: Zap,
          features: [
            `Process up to 25 jobs at once`,
            'Smart global settings',
            'Live progress tracking',
            'Batch analytics dashboard',
            'One-click downloads'
          ],
          estimatedTime: estimatedProcessingTime.batch,
          useCase: 'Multiple jobs',
          available: true,
          proOnly: false,
          recommended: jobCount > 1
        },
        {
          mode: 'precision',
          title: 'Precision Mode',
          subtitle: 'Perfect Control',
          description: 'Fine-tune every detail with real-time previews. Ideal for your most important applications.',
          icon: Settings,
          features: [
            'Bullet-by-bullet control',
            'Real-time score updates',
            'Before/after previews',
            'Custom editing tools',
            'Advanced analytics'
          ],
          estimatedTime: estimatedProcessingTime.precision,
          useCase: 'Important jobs',
          available: true,
          proOnly: false,
          recommended: jobCount === 1
        }
      ];
    } else {
      return [
        {
          mode: 'batch',
          title: 'Quick Mode',
          subtitle: 'Fast & Smart',
          description: 'Get your resume optimized quickly with our smart automation. Perfect for getting started.',
          icon: Zap,
          features: [
            'Process 1 job quickly',
            'Smart optimization',
            'Instant results',
            'Basic analytics',
            'PDF download'
          ],
          estimatedTime: estimatedProcessingTime.batch,
          useCase: 'Quick results',
          available: true,
          proOnly: false,
          recommended: true
        },
        {
          mode: 'precision',
          title: 'Precision Mode',
          subtitle: 'Pro Feature',
          description: 'Unlock granular control and advanced features. Get the most out of every application.',
          icon: Settings,
          features: [
            'Bullet-by-bullet control',
            'Real-time previews',
            'Advanced analytics',
            'Custom editing',
            'Unlimited processing'
          ],
          estimatedTime: estimatedProcessingTime.precision,
          useCase: 'Maximum control',
          available: false,
          proOnly: true,
          recommended: false
        }
      ];
    }
  };

  const modes = getMobileModesConfig();

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    updateMobileUI({ selectedMode: mode });
    onModeSelect(mode);
  };

  const handleUpgradeClick = () => {
    setShowUpgradeFlow(true);
    if (onUpgradeClick) {
      onUpgradeClick();
    }
  };

  const handleUpgrade = async (plan) => {
    // Implement upgrade logic here
    console.log('Upgrading to:', plan);
    setShowUpgradeFlow(false);
  };

  return (
    <DeviceOptimizedLayout deviceType={deviceType}>
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className={`space-y-6 ${className}`}
      >
        {/* Header */}
        <motion.div variants={staggerItem} className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Choose Your Approach
          </h2>
          <p className="text-gray-600 text-sm sm:text-base">
            Select the mode that matches your needs and time availability
          </p>
        </motion.div>

        {/* Device Type Indicator (Development Only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="flex justify-center">
            <div className="flex items-center gap-2 bg-gray-100 rounded-full px-3 py-1 text-xs text-gray-600">
              {deviceType === 'mobile' && <Smartphone className="w-3 h-3" />}
              {deviceType === 'tablet' && <Tablet className="w-3 h-3" />}
              {deviceType === 'desktop' && <Monitor className="w-3 h-3" />}
              {deviceType} layout
            </div>
          </div>
        )}

        {/* Mode Selection */}
        <motion.div variants={staggerItem}>
          {deviceType === 'mobile' ? (
            <SwipeableModeSelector
              modes={modes}
              selectedMode={selectedMode}
              onModeSelect={handleModeSelect}
              onUpgradeClick={handleUpgradeClick}
              tier={tier}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {modes.map((mode) => (
                <MobileModeCard
                  key={mode.mode}
                  {...mode}
                  onSelect={handleModeSelect}
                  onUpgradeClick={handleUpgradeClick}
                  isSelected={selectedMode === mode.mode}
                  isActive={true}
                  tier={tier}
                />
              ))}
            </div>
          )}
        </motion.div>

        {/* Action Buttons */}
        <motion.div variants={staggerItem} className="flex flex-col sm:flex-row gap-3">
          <Button
            variant="outline"
            onClick={() => setShowComparison(true)}
            className="flex-1 h-12 border-gray-300 text-gray-700 hover:bg-gray-50 active:scale-95"
          >
            <Info className="w-4 h-4 mr-2" />
            Compare Features
          </Button>
          
          {!isProUser && (
            <Button
              onClick={handleUpgradeClick}
              className="flex-1 h-12 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white active:scale-95"
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade to Pro
            </Button>
          )}
        </motion.div>

        {/* Usage Indicator for Free Users */}
        {!isProUser && (
          <motion.div variants={staggerItem}>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-sm text-gray-600 mb-2">
                Weekly Usage: {weeklyUsage} / {weeklyLimit}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(weeklyUsage / weeklyLimit) * 100}%` }}
                />
              </div>
              {weeklyUsage >= weeklyLimit && (
                <p className="text-xs text-amber-600 mt-2">
                  Weekly limit reached. Upgrade for unlimited access.
                </p>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Feature Comparison Modal */}
      <MobileFeatureComparison
        tier={tier}
        isVisible={showComparison}
        onClose={() => setShowComparison(false)}
      />

      {/* Upgrade Flow Modal */}
      <MobileUpgradeFlow
        isVisible={showUpgradeFlow}
        onClose={() => setShowUpgradeFlow(false)}
        onUpgrade={handleUpgrade}
        context="mode-selection"
      />
    </DeviceOptimizedLayout>
  );
}

export default MobileOptimizedModeSelection;