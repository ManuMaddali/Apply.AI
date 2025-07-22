import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  fetchUsageStatistics, 
  getUsagePercentage, 
  getUsageStatus,
  formatUsageResetDate 
} from '../utils/subscriptionUtils';

const UsageIndicator = ({ 
  type = 'weekly', 
  showLabel = true, 
  showProgress = true,
  compact = false,
  className = ''
}) => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUsageData = async () => {
      if (!isAuthenticated || !user) {
        setLoading(false);
        return;
      }

      try {
        const data = await fetchUsageStatistics(authenticatedRequest);
        setUsageData(data);
      } catch (error) {
        console.error('Failed to load usage data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUsageData();

    // Listen for usage updates
    const handleUsageUpdate = () => loadUsageData();
    window.addEventListener('usageUpdated', handleUsageUpdate);
    return () => window.removeEventListener('usageUpdated', handleUsageUpdate);
  }, [isAuthenticated, user, authenticatedRequest]);

  if (!isAuthenticated || loading) {
    return compact ? null : (
      <div className={`animate-pulse ${className}`}>
        <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
        <div className="h-2 bg-gray-200 rounded w-full"></div>
      </div>
    );
  }

  const isProUser = user?.subscription_tier === 'pro' || usageData?.subscription_tier === 'pro';
  const weeklyUsage = usageData?.weekly_usage_count || 0;
  const weeklyLimit = usageData?.current_limits?.weekly_sessions || 5;
  const usagePercentage = getUsagePercentage(weeklyUsage, isProUser ? -1 : weeklyLimit);
  const usageStatus = getUsageStatus(weeklyUsage, isProUser ? -1 : weeklyLimit);
  const resetDate = formatUsageResetDate(usageData?.weekly_usage_reset);

  const getStatusColor = () => {
    switch (usageStatus) {
      case 'exceeded':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      case 'unlimited':
        return 'text-purple-600';
      default:
        return 'text-gray-900';
    }
  };

  const getProgressColor = () => {
    switch (usageStatus) {
      case 'exceeded':
        return 'bg-gradient-to-r from-red-500 to-red-600';
      case 'warning':
        return 'bg-gradient-to-r from-yellow-500 to-orange-500';
      case 'unlimited':
        return 'bg-gradient-to-r from-purple-500 to-pink-600';
      default:
        return 'bg-gradient-to-r from-blue-500 to-cyan-600';
    }
  };

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 ${className}`}>
        {isProUser ? (
          <div className="flex items-center gap-1 text-purple-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span className="text-sm font-medium">Unlimited</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium ${getStatusColor()}`}>
              {weeklyUsage}/{weeklyLimit}
            </span>
            {showProgress && (
              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                <div 
                  className={`h-1.5 rounded-full transition-all duration-300 ${getProgressColor()}`}
                  style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                ></div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {showLabel && (
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            {type === 'weekly' ? 'Weekly Sessions' : 'Usage'}
          </span>
          <span className={`text-sm font-semibold ${getStatusColor()}`}>
            {isProUser ? (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                Unlimited
              </div>
            ) : (
              `${weeklyUsage}/${weeklyLimit}`
            )}
          </span>
        </div>
      )}
      
      {showProgress && (
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className={`h-2.5 rounded-full transition-all duration-300 ${getProgressColor()}`}
            style={{ width: `${isProUser ? 100 : Math.min(usagePercentage, 100)}%` }}
          ></div>
        </div>
      )}
      
      {/* Status Message */}
      <div className={`text-xs ${getStatusColor()}`}>
        {usageStatus === 'exceeded' ? (
          <div className="flex items-center gap-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Weekly limit reached
          </div>
        ) : usageStatus === 'warning' ? (
          <div className="flex items-center gap-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            {weeklyLimit - weeklyUsage} sessions remaining
          </div>
        ) : usageStatus === 'unlimited' ? (
          'Process unlimited resumes with Pro'
        ) : (
          `${weeklyLimit - weeklyUsage} sessions remaining this week`
        )}
      </div>

      {/* Reset Information */}
      {resetDate && !isProUser && (
        <div className="text-xs text-gray-500">
          Resets {resetDate}
        </div>
      )}
    </div>
  );
};

// Circular progress indicator variant
export const CircularUsageIndicator = ({ 
  size = 60, 
  strokeWidth = 4,
  showLabel = true,
  className = ''
}) => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [usageData, setUsageData] = useState(null);

  useEffect(() => {
    const loadUsageData = async () => {
      if (!isAuthenticated || !user) return;

      try {
        const data = await fetchUsageStatistics(authenticatedRequest);
        setUsageData(data);
      } catch (error) {
        console.error('Failed to load usage data:', error);
      }
    };

    loadUsageData();

    const handleUsageUpdate = () => loadUsageData();
    window.addEventListener('usageUpdated', handleUsageUpdate);
    return () => window.removeEventListener('usageUpdated', handleUsageUpdate);
  }, [isAuthenticated, user, authenticatedRequest]);

  if (!isAuthenticated) return null;

  const isProUser = user?.subscription_tier === 'pro' || usageData?.subscription_tier === 'pro';
  const weeklyUsage = usageData?.weekly_usage_count || 0;
  const weeklyLimit = usageData?.current_limits?.weekly_sessions || 5;
  const usagePercentage = getUsagePercentage(weeklyUsage, isProUser ? -1 : weeklyLimit);
  const usageStatus = getUsageStatus(weeklyUsage, isProUser ? -1 : weeklyLimit);

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = isProUser ? 0 : circumference - (usagePercentage / 100) * circumference;

  const getStrokeColor = () => {
    switch (usageStatus) {
      case 'exceeded':
        return '#ef4444';
      case 'warning':
        return '#f59e0b';
      case 'unlimited':
        return '#8b5cf6';
      default:
        return '#3b82f6';
    }
  };

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative">
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getStrokeColor()}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900">
              {isProUser ? '∞' : weeklyUsage}
            </div>
            {!isProUser && (
              <div className="text-xs text-gray-500">
                /{weeklyLimit}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {showLabel && (
        <div className="mt-2 text-center">
          <div className="text-xs font-medium text-gray-700">
            {isProUser ? 'Unlimited' : 'Weekly'}
          </div>
        </div>
      )}
    </div>
  );
};

// Monthly usage indicator variant
export const MonthlyUsageIndicator = ({ current, limit, resetDate, type = 'sessions', ...props }) => (
  <UsageIndicator
    current={current}
    limit={limit}
    type={`monthly ${type}`}
    resetDate={resetDate}
    {...props}
  />
);

// Compact usage indicator for headers/badges
export const CompactUsageIndicator = ({ current, limit, type = 'sessions' }) => {
  const isUnlimited = limit === -1;
  const status = getUsageStatus(current, limit);
  
  const getStatusColor = () => {
    switch (status) {
      case 'exceeded':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'unlimited':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor()}`}>
      {isUnlimited ? (
        <>
          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          ∞
        </>
      ) : (
        `${current}/${limit}`
      )}
    </span>
  );
};

export default UsageIndicator;