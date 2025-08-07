import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  ArrowUp, 
  X, 
  Crown, 
  Star, 
  TrendingUp,
  Clock,
  CheckCircle,
  Sparkles
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { TierBadge } from './ui/tier-badge';

/**
 * UpgradePrompt Component
 * Contextual upgrade prompts based on usage and tier status
 */
export function UpgradePrompt({ 
  context = 'general',
  usageStatus = 'normal',
  weeklyUsage = 0,
  weeklyLimit = 5,
  remainingSessions = 5,
  onUpgradeClick,
  onDismiss,
  showDismiss = false,
  size = 'default',
  variant = 'card',
  className = '',
  ...props 
}) {
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  // Context-specific configurations
  const contextConfig = {
    general: {
      title: 'Upgrade to Pro',
      description: 'Unlock unlimited features and advanced capabilities',
      icon: Zap,
      features: ['Unlimited sessions', 'Advanced formatting', 'Premium templates']
    },
    limit_reached: {
      title: 'Weekly Limit Reached!',
      description: 'You\'ve used all your free sessions this week',
      icon: Clock,
      features: ['Unlimited sessions', 'No weekly limits', 'Process anytime']
    },
    approaching_limit: {
      title: 'Almost at Your Limit',
      description: `Only ${remainingSessions} session${remainingSessions === 1 ? '' : 's'} remaining this week`,
      icon: TrendingUp,
      features: ['Unlimited sessions', 'Never worry about limits', 'Premium features']
    },
    feature_locked: {
      title: 'Pro Feature',
      description: 'This feature requires a Pro subscription',
      icon: Crown,
      features: ['Advanced formatting', 'Cover letters', 'Analytics dashboard']
    },
    bulk_processing: {
      title: 'Bulk Processing Available',
      description: 'Process multiple resumes at once with Pro',
      icon: Sparkles,
      features: ['Bulk processing', 'Batch operations', 'Time-saving automation']
    }
  };

  const config = contextConfig[context] || contextConfig.general;
  const Icon = config.icon;

  // Status-based styling
  const getStatusStyles = () => {
    switch (usageStatus) {
      case 'exceeded':
        return {
          container: 'border-red-300 bg-red-50',
          button: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800',
          accent: 'text-red-700',
          iconBg: 'bg-red-100'
        };
      case 'warning':
        return {
          container: 'border-amber-300 bg-amber-50',
          button: 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700',
          accent: 'text-amber-700',
          iconBg: 'bg-amber-100'
        };
      default:
        return {
          container: 'border-purple-300 bg-purple-50',
          button: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700',
          accent: 'text-purple-700',
          iconBg: 'bg-purple-100'
        };
    }
  };

  const styles = getStatusStyles();

  // Size variants
  const sizeConfig = {
    sm: {
      container: 'p-3',
      title: 'text-sm font-semibold',
      description: 'text-xs',
      button: 'text-xs px-3 py-1.5',
      icon: 'w-4 h-4'
    },
    default: {
      container: 'p-4',
      title: 'text-base font-semibold',
      description: 'text-sm',
      button: 'text-sm px-4 py-2',
      icon: 'w-5 h-5'
    },
    lg: {
      container: 'p-6',
      title: 'text-lg font-bold',
      description: 'text-base',
      button: 'text-base px-6 py-3',
      icon: 'w-6 h-6'
    }
  };

  const sizeStyles = sizeConfig[size];

  // Render variants
  if (variant === 'banner') {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className={`relative flex items-center justify-between ${sizeStyles.container} rounded-lg border-2 border-dashed ${styles.container} ${className}`}
        {...props}
      >
        {showDismiss && (
          <button
            onClick={handleDismiss}
            className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Dismiss upgrade prompt"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${styles.iconBg}`}>
            <Icon className={`${sizeStyles.icon} ${styles.accent}`} />
          </div>
          <div>
            <h4 className={`${sizeStyles.title} ${styles.accent}`}>
              {config.title}
            </h4>
            <p className={`${sizeStyles.description} text-gray-600 mt-1`}>
              {config.description}
            </p>
          </div>
        </div>
        
        <Button
          onClick={onUpgradeClick}
          className={`${sizeStyles.button} ${styles.button} text-white shadow-lg hover:shadow-xl transition-all`}
        >
          <ArrowUp className="w-4 h-4 mr-2" />
          Upgrade Now
        </Button>
      </motion.div>
    );
  }

  if (variant === 'inline') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={`inline-flex items-center gap-2 ${className}`}
        {...props}
      >
        <TierBadge tier="pro" size="sm" />
        <span className="text-sm text-gray-600">required</span>
        <Button
          onClick={onUpgradeClick}
          variant="outline"
          size="sm"
          className="border-purple-300 text-purple-700 hover:bg-purple-50"
        >
          Upgrade
        </Button>
      </motion.div>
    );
  }

  // Default card variant
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.3 }}
    >
      <Card className={`relative border-2 border-dashed ${styles.container} ${className}`} {...props}>
        {showDismiss && (
          <button
            onClick={handleDismiss}
            className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition-colors z-10"
            aria-label="Dismiss upgrade prompt"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        
        <CardContent className={sizeStyles.container}>
          <div className="text-center space-y-4">
            {/* Icon and Title */}
            <div className="space-y-3">
              <div className={`inline-flex p-3 rounded-full ${styles.iconBg}`}>
                <Icon className={`${sizeStyles.icon} ${styles.accent}`} />
              </div>
              <div>
                <h3 className={`${sizeStyles.title} ${styles.accent}`}>
                  {config.title}
                </h3>
                <p className={`${sizeStyles.description} text-gray-600 mt-2`}>
                  {config.description}
                </p>
              </div>
            </div>

            {/* Features List */}
            <div className="space-y-2">
              {config.features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + (index * 0.1) }}
                  className="flex items-center gap-2 text-sm text-gray-600"
                >
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>{feature}</span>
                </motion.div>
              ))}
            </div>

            {/* Action Button */}
            <Button
              onClick={onUpgradeClick}
              className={`w-full ${sizeStyles.button} ${styles.button} text-white shadow-lg hover:shadow-xl transition-all`}
            >
              <Zap className="w-4 h-4 mr-2" />
              Upgrade to Pro
            </Button>

            {/* Additional Info */}
            <p className="text-xs text-gray-500">
              Cancel anytime • No commitment required
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

/**
 * ContextualUpgradePrompt Component
 * Automatically determines the appropriate upgrade prompt based on context
 */
export function ContextualUpgradePrompt({ 
  weeklyUsage = 0,
  weeklyLimit = 5,
  isProUser = false,
  hasExceededLimit = false,
  isApproachingLimit = false,
  onUpgradeClick,
  ...props 
}) {
  if (isProUser) return null;

  let context = 'general';
  let usageStatus = 'normal';

  if (hasExceededLimit) {
    context = 'limit_reached';
    usageStatus = 'exceeded';
  } else if (isApproachingLimit) {
    context = 'approaching_limit';
    usageStatus = 'warning';
  }

  const remainingSessions = Math.max(0, weeklyLimit - weeklyUsage);

  return (
    <UpgradePrompt
      context={context}
      usageStatus={usageStatus}
      weeklyUsage={weeklyUsage}
      weeklyLimit={weeklyLimit}
      remainingSessions={remainingSessions}
      onUpgradeClick={onUpgradeClick}
      {...props}
    />
  );
}

/**
 * FeatureLockedPrompt Component
 * Specific prompt for locked features
 */
export function FeatureLockedPrompt({ 
  featureName = 'feature',
  onUpgradeClick,
  ...props 
}) {
  return (
    <UpgradePrompt
      context="feature_locked"
      variant="inline"
      onUpgradeClick={onUpgradeClick}
      {...props}
    />
  );
}

export default UpgradePrompt;