import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Crown, Star } from 'lucide-react';
import { Badge } from './badge';

/**
 * TierBadge Component
 * Displays subscription tier with appropriate styling and icons
 */
export function TierBadge({ 
  tier = 'free', 
  isActive = true,
  size = 'default',
  variant = 'default',
  showIcon = true,
  animated = false,
  className = '',
  ...props 
}) {
  const isProUser = tier === 'pro' && isActive;
  
  // Tier configuration
  const tierConfig = {
    free: {
      label: 'Free',
      icon: Star,
      colors: {
        default: 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800 border-blue-200',
        outline: 'border-blue-300 text-blue-700 hover:bg-blue-50',
        solid: 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white'
      }
    },
    pro: {
      label: 'Pro',
      icon: isActive ? Crown : Zap,
      colors: {
        default: 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 border-purple-200',
        outline: 'border-purple-300 text-purple-700 hover:bg-purple-50',
        solid: 'bg-gradient-to-r from-purple-500 to-pink-600 text-white'
      }
    }
  };

  const config = tierConfig[tier] || tierConfig.free;
  const Icon = config.icon;
  
  // Size variants
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    default: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    default: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  const badgeContent = (
    <div className="flex items-center gap-1.5">
      {showIcon && (
        <Icon 
          className={`${iconSizes[size]} ${animated && isProUser ? 'animate-pulse' : ''}`}
          aria-hidden="true"
        />
      )}
      <span className="font-semibold">{config.label}</span>
      {!isActive && tier === 'pro' && (
        <span className="text-xs opacity-75">(Expired)</span>
      )}
    </div>
  );

  const badgeClasses = `
    ${sizeClasses[size]}
    ${config.colors[variant]}
    ${className}
  `;

  if (animated) {
    return (
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Badge 
          className={badgeClasses}
          {...props}
        >
          {badgeContent}
        </Badge>
      </motion.div>
    );
  }

  return (
    <Badge 
      className={badgeClasses}
      {...props}
    >
      {badgeContent}
    </Badge>
  );
}

/**
 * TierIndicator Component
 * More detailed tier display with features and limitations
 */
export function TierIndicator({ 
  tier = 'free',
  isActive = true,
  weeklyUsage = 0,
  weeklyLimit = 5,
  showUsage = true,
  showFeatures = false,
  onUpgradeClick,
  className = '',
  ...props 
}) {
  const isProUser = tier === 'pro' && isActive;
  
  const features = {
    free: [
      'Up to 5 resumes per week',
      'Basic formatting',
      'Standard templates'
    ],
    pro: [
      'Unlimited resumes',
      'Advanced formatting',
      'Premium templates',
      'Cover letter generation',
      'Analytics dashboard'
    ]
  };

  return (
    <motion.div
      className={`p-4 rounded-xl border-2 border-dashed transition-all duration-300 ${
        isProUser 
          ? 'border-purple-300 bg-gradient-to-br from-purple-50 to-pink-50' 
          : 'border-blue-300 bg-gradient-to-br from-blue-50 to-cyan-50'
      } ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      <div className="flex items-center justify-between mb-3">
        <TierBadge 
          tier={tier}
          isActive={isActive}
          size="lg"
          animated={true}
        />
        {!isProUser && onUpgradeClick && (
          <button
            onClick={onUpgradeClick}
            className="text-sm font-medium text-purple-600 hover:text-purple-700 transition-colors"
          >
            Upgrade →
          </button>
        )}
      </div>

      {showUsage && (
        <div className="mb-3">
          {isProUser ? (
            <div className="flex items-center gap-2 text-sm text-purple-700">
              <Zap className="w-4 h-4" />
              <span className="font-medium">Unlimited sessions</span>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Weekly usage:</span>
                <span className="font-medium">{weeklyUsage}/{weeklyLimit}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-cyan-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min((weeklyUsage / weeklyLimit) * 100, 100)}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {showFeatures && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">
            {isProUser ? 'Pro Features:' : 'Free Features:'}
          </h4>
          <ul className="space-y-1">
            {features[tier].map((feature, index) => (
              <li key={index} className="flex items-center gap-2 text-xs text-gray-600">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  isProUser ? 'bg-purple-500' : 'bg-blue-500'
                }`} />
                {feature}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}

export default TierBadge;