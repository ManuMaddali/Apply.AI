import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Clock, Zap, ArrowUp, TrendingUp, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { TierBadge } from './ui/tier-badge';
import { UsageDonutChart } from './ui/donut-chart';
import { ContextualUpgradePrompt } from './UpgradePrompt';
import { useSubscription } from '../hooks/useSubscription';
import { formatUsageResetDate, getUsagePercentage } from '../utils/subscriptionUtils';
import { announceToScreenReader, A11yUtils } from '../utils/keyboardNavigation';

/**
 * CountdownTimer Component
 * Shows time remaining until usage reset with purple progress indicator
 */
function CountdownTimer({ resetDate }) {
  const [timeRemaining, setTimeRemaining] = useState('');
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [formattedResetDate, setFormattedResetDate] = useState('');
  const timerRef = useRef(null);

  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date();
      const timeDiff = resetDate - now;

      if (timeDiff <= 0) {
        setTimeRemaining('Resetting...');
        setProgressPercentage(100);
        return;
      }

      const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

      // Format time remaining with more precision
      if (days > 0) {
        setTimeRemaining(`${days}d ${hours}h`);
      } else if (hours > 0) {
        setTimeRemaining(`${hours}h ${minutes}m`);
      } else if (minutes > 0) {
        setTimeRemaining(`${minutes}m ${seconds}s`);
      } else {
        setTimeRemaining(`${seconds}s`);
      }

      // Format reset date
      setFormattedResetDate(new Intl.DateTimeFormat('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(resetDate));

      // Calculate progress (assuming weekly reset, so 7 days total)
      const totalWeekMs = 7 * 24 * 60 * 60 * 1000;
      const elapsedMs = totalWeekMs - timeDiff;
      const progress = Math.min(100, Math.max(0, (elapsedMs / totalWeekMs) * 100));
      setProgressPercentage(progress);
    };

    updateCountdown();
    // Update more frequently for a smoother experience
    const interval = setInterval(updateCountdown, 1000); // Update every second

    return () => clearInterval(interval);
  }, [resetDate]);

  return (
    <motion.div 
      ref={timerRef}
      className="space-y-3"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.5 }}
      role="timer"
      aria-label="Usage reset countdown"
    >
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <Calendar className="w-4 h-4" aria-hidden="true" />
          <span>Resets in:</span>
        </div>
        <div className="flex items-center gap-2">
          <span 
            className="font-medium text-purple-600"
            aria-live="polite"
            aria-label={`Time remaining: ${timeRemaining}`}
          >
            {timeRemaining}
          </span>
          <div 
            className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden"
            role="progressbar"
            aria-valuenow={Math.round(progressPercentage)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Week progress: ${Math.round(progressPercentage)} percent complete`}
          >
            <motion.div
              className="h-full bg-purple-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>
      
      {/* Reset date display */}
      <div className="flex justify-between items-center text-xs text-gray-500">
        <span>Reset date:</span>
        <span 
          className="font-medium"
          aria-label={`Usage resets on ${formattedResetDate}`}
        >
          {formattedResetDate}
        </span>
      </div>
      
      {/* Visual progress bar with tooltip */}
      <div className="relative pt-1">
        <div className="flex mb-1 items-center justify-between">
          <div className="text-xs text-gray-500">Week progress</div>
          <div 
            className="text-xs text-purple-600 font-semibold"
            aria-label={`${Math.round(progressPercentage)} percent of week completed`}
          >
            {Math.round(progressPercentage)}%
          </div>
        </div>
        <div 
          className="overflow-hidden h-2 text-xs flex rounded-full bg-purple-100"
          role="progressbar"
          aria-valuenow={Math.round(progressPercentage)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Weekly progress: ${Math.round(progressPercentage)} percent`}
        >
          <motion.div
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-500"
            initial={{ width: 0 }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </div>
    </motion.div>
  );
}

/**
 * UsageSidebarCard Component
 * Displays usage tracking with donut chart, countdown timer, and upgrade prompts
 */
export function UsageSidebarCard({ 
  className,
  onUpgradeClick,
  showUpgradePrompts = true,
  ...props 
}) {
  const {
    weeklyUsage,
    weeklyLimit,
    isProUser,
    remainingSessions,
    hasExceededLimit,
    isApproachingLimit,
    loading
  } = useSubscription();
  
  const cardRef = useRef(null);
  const chartRef = useRef(null);
  const upgradeButtonRef = useRef(null);

  // Calculate reset date (assuming weekly reset on Mondays)
  const getResetDate = () => {
    const now = new Date();
    const daysUntilMonday = (8 - now.getDay()) % 7 || 7;
    const resetDate = new Date(now);
    resetDate.setDate(now.getDate() + daysUntilMonday);
    resetDate.setHours(0, 0, 0, 0);
    return resetDate;
  };

  const resetDate = getResetDate();

  // Usage status for styling
  const getUsageStatus = () => {
    if (isProUser) return 'unlimited';
    if (hasExceededLimit) return 'exceeded';
    if (isApproachingLimit) return 'warning';
    return 'normal';
  };

  const usageStatus = getUsageStatus();

  // Status colors and messages
  const getStatusConfig = () => {
    switch (usageStatus) {
      case 'unlimited':
        return {
          color: '#A78BFA',
          bgColor: 'bg-purple-50',
          textColor: 'text-purple-700',
          message: 'Unlimited sessions',
          icon: Zap
        };
      case 'exceeded':
        return {
          color: '#EF4444',
          bgColor: 'bg-red-50',
          textColor: 'text-red-700',
          message: 'Limit reached',
          icon: Clock
        };
      case 'warning':
        return {
          color: '#F59E0B',
          bgColor: 'bg-amber-50',
          textColor: 'text-amber-700',
          message: 'Almost at limit',
          icon: TrendingUp
        };
      default:
        return {
          color: '#A78BFA',
          bgColor: 'bg-purple-50',
          textColor: 'text-purple-700',
          message: 'Good usage',
          icon: TrendingUp
        };
    }
  };

  const statusConfig = getStatusConfig();
  const StatusIcon = statusConfig.icon;

  if (loading) {
    return (
      <Card 
        className={className} 
        {...props}
        role="region"
        aria-label="Usage tracking (loading)"
      >
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-5 h-5 bg-gray-200 rounded animate-pulse" aria-hidden="true" />
            <div className="w-20 h-5 bg-gray-200 rounded animate-pulse" aria-hidden="true" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-center">
            <div 
              className="w-24 h-24 bg-gray-200 rounded-full animate-pulse" 
              aria-hidden="true"
              role="img"
              aria-label="Loading usage chart"
            />
          </div>
          <div className="space-y-2" aria-hidden="true">
            <div className="w-full h-4 bg-gray-200 rounded animate-pulse" />
            <div className="w-3/4 h-4 bg-gray-200 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <Card 
        ref={cardRef}
        className={className} 
        {...props}
        role="region"
        aria-label="Usage tracking and subscription information"
      >
        <CardHeader className="pb-3">
          <CardTitle 
            id="usage-tracking-title"
            className="text-lg flex items-center gap-2"
          >
            <StatusIcon className="w-5 h-5 text-purple-600" aria-hidden="true" />
            Usage Tracking
            <div className="ml-auto">
              <TierBadge 
                tier={isProUser ? 'pro' : 'free'}
                isActive={isProUser}
                size="sm"
                animated={true}
                aria-label={`${isProUser ? 'Pro' : 'Free'} subscription ${isProUser ? 'active' : ''}`}
              />
            </div>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6" aria-labelledby="usage-tracking-title">
          {/* Usage Donut Chart */}
          <div className="flex flex-col items-center space-y-3">
            <motion.div
              ref={chartRef}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              role="img"
              aria-label={`Usage chart: ${weeklyUsage} of ${isProUser ? 'unlimited' : weeklyLimit} sessions used this week`}
            >
              <UsageDonutChart
                used={weeklyUsage}
                limit={isProUser ? 999 : weeklyLimit}
                size={100}
                strokeWidth={8}
                resetDate={resetDate}
                showHoverDetails={true}
                animated={true}
                duration={1.5}
              />
            </motion.div>
            
            {/* Usage Status */}
            <motion.div 
              className={`px-3 py-1 rounded-full text-sm font-medium ${statusConfig.bgColor} ${statusConfig.textColor}`}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.6 }}
              role="status"
              aria-live="polite"
              aria-label={`Usage status: ${statusConfig.message}`}
            >
              {statusConfig.message}
            </motion.div>
          </div>

          {/* Usage Details */}
          <div className="space-y-3">
            {!isProUser && (
              <motion.div 
                className="flex justify-between items-center text-sm"
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.7 }}
              >
                <span className="text-gray-600">Sessions used:</span>
                <span className="font-medium">
                  {weeklyUsage} of {weeklyLimit}
                </span>
              </motion.div>
            )}
            
            {!isProUser && (
              <motion.div 
                className="flex justify-between items-center text-sm"
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.8 }}
              >
                <span className="text-gray-600">Remaining:</span>
                <span className={`font-medium ${remainingSessions === 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {remainingSessions} sessions
                </span>
              </motion.div>
            )}
            
            {!isProUser && (
              <motion.div 
                className="flex justify-between items-center text-sm"
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.9 }}
              >
                <span className="text-gray-600">Usage percentage:</span>
                <span className={`font-medium ${
                  getUsagePercentage(weeklyUsage, weeklyLimit) >= 80 ? 'text-amber-600' : 
                  getUsagePercentage(weeklyUsage, weeklyLimit) >= 100 ? 'text-red-600' : 'text-purple-600'
                }`}>
                  {Math.round(getUsagePercentage(weeklyUsage, weeklyLimit))}%
                </span>
              </motion.div>
            )}

            {isProUser && (
              <motion.div 
                className="text-center"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.7 }}
              >
                <div className="flex items-center justify-center gap-2 text-purple-600">
                  <Zap className="w-4 h-4" />
                  <span className="font-medium">Unlimited Sessions</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Process as many resumes as you need
                </p>
              </motion.div>
            )}
          </div>

          {/* Countdown Timer - Sub-task 8.2 */}
          {!isProUser && (
            <motion.div 
              className="pt-3 border-t border-gray-100"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.0 }}
            >
              <CountdownTimer resetDate={resetDate} />
            </motion.div>
          )}

          {/* Contextual Upgrade Prompts */}
          {showUpgradePrompts && !isProUser && (
            <motion.div 
              className="pt-4 border-t border-gray-100"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 1.2 }}
            >
              <ContextualUpgradePrompt
                weeklyUsage={weeklyUsage}
                weeklyLimit={weeklyLimit}
                isProUser={isProUser}
                hasExceededLimit={hasExceededLimit}
                isApproachingLimit={isApproachingLimit}
                onUpgradeClick={onUpgradeClick}
                size="sm"
              />
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default UsageSidebarCard;