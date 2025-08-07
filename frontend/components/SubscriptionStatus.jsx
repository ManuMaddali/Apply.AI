import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../utils/api';
import { TierBadge, TierIndicator } from './ui/tier-badge';
import { ContextualUpgradePrompt } from './UpgradePrompt';

const SubscriptionStatus = ({ onUpgradeClick, showUpgradePrompt = true }) => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch subscription status and usage data
  const fetchSubscriptionData = async () => {
    if (!isAuthenticated || !user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      console.log('🔍 [SubscriptionStatus] Fetching subscription data...');
      console.log('🔍 [SubscriptionStatus] API_BASE_URL:', API_BASE_URL);
      console.log('🔍 [SubscriptionStatus] User authenticated:', isAuthenticated);

      // Fetch subscription status
      try {
        console.log('🔍 [SubscriptionStatus] Fetching subscription status...');
        const statusResponse = await authenticatedRequest(`${API_BASE_URL}/api/subscription/status`);
        console.log('🔍 [SubscriptionStatus] Status response:', statusResponse.status);
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          console.log('🔍 [SubscriptionStatus] Status data:', statusData);
          setSubscriptionData(statusData);
        } else {
          const errorText = await statusResponse.text();
          console.error('❌ [SubscriptionStatus] Status request failed:', statusResponse.status, errorText);
          throw new Error(`Status request failed: ${statusResponse.status}`);
        }
      } catch (statusError) {
        console.error('❌ [SubscriptionStatus] Status request error:', statusError);
        throw new Error(`Failed to fetch subscription status: ${statusError.message}`);
      }

      // Fetch usage statistics
      try {
        console.log('🔍 [SubscriptionStatus] Fetching usage statistics...');
        const usageResponse = await authenticatedRequest(`${API_BASE_URL}/api/subscription/usage`);
        console.log('🔍 [SubscriptionStatus] Usage response:', usageResponse.status);
        
        if (usageResponse.ok) {
          const usageStats = await usageResponse.json();
          console.log('🔍 [SubscriptionStatus] Usage data:', usageStats);
          setUsageData(usageStats);
        } else {
          const errorText = await usageResponse.text();
          console.error('❌ [SubscriptionStatus] Usage request failed:', usageResponse.status, errorText);
          throw new Error(`Usage request failed: ${usageResponse.status}`);
        }
      } catch (usageError) {
        console.error('❌ [SubscriptionStatus] Usage request error:', usageError);
        throw new Error(`Failed to fetch usage statistics: ${usageError.message}`);
      }

      console.log('✅ [SubscriptionStatus] All data fetched successfully');

    } catch (err) {
      console.error('❌ [SubscriptionStatus] Overall error:', err);
      setError(`Failed to load subscription information: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptionData();
  }, [isAuthenticated, user]);

  // Refresh data when user processes resumes
  useEffect(() => {
    const handleUsageUpdate = () => {
      fetchSubscriptionData();
    };

    // Listen for custom events when usage is updated
    window.addEventListener('usageUpdated', handleUsageUpdate);
    return () => window.removeEventListener('usageUpdated', handleUsageUpdate);
  }, []);

  if (!isAuthenticated || !user) {
    return null;
  }

  if (loading) {
    return (
      <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6">
        <div className="animate-pulse">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-32"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !subscriptionData && !usageData) {
    // Try to use fallback data from user object instead of showing error
    if (user && (user.subscription_tier || user.weekly_usage_count !== undefined)) {
      console.log('🔄 [SubscriptionStatus] Using fallback data from user object');
      const fallbackData = {
        subscription_tier: user.subscription_tier || 'free',
        is_pro_active: user.is_pro_active || false,
        weekly_usage_count: user.weekly_usage_count || 0,
        usage_limits: user.usage_limits || { weekly_sessions: 5 },
        weekly_usage_reset: user.weekly_usage_reset
      };
      
      // Use fallback data and clear error
      setSubscriptionData(fallbackData);
      setUsageData(fallbackData);
      setError(null);
    } else {
      // Only show error if we truly have no fallback data
      return (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-700 text-sm">{error}</span>
            </div>
            <button
              onClick={() => {
                setError(null);
                fetchSubscriptionData();
              }}
              className="text-red-600 hover:text-red-800 text-sm font-medium"
            >
              Retry
            </button>
          </div>
        </div>
      );
    }
  }

  const isProUser = subscriptionData?.is_pro_active || user?.subscription_tier === 'pro';
  const weeklyUsage = usageData?.weekly_usage_count || user?.weekly_usage_count || 0;
  const weeklyLimit = subscriptionData?.usage_limits?.weekly_sessions || 5;
  const usagePercentage = isProUser ? 0 : Math.min((weeklyUsage / weeklyLimit) * 100, 100);
  
  // Determine if user is approaching limit (80% or more)
  const isApproachingLimit = !isProUser && usagePercentage >= 80;
  const hasExceededLimit = !isProUser && weeklyUsage >= weeklyLimit;

  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 transition-all duration-300 hover:shadow-xl hover:bg-white/90">
      {/* Header with tier badge */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl shadow-lg ${
            isProUser 
              ? 'bg-gradient-to-r from-purple-500 to-pink-600' 
              : 'bg-gradient-to-r from-blue-500 to-cyan-600'
          }`}>
            {isProUser ? (
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <TierBadge 
                tier={isProUser ? 'pro' : 'free'}
                isActive={isProUser && !subscriptionData?.cancel_at_period_end}
                size="default"
                animated={true}
              />
              {subscriptionData?.cancel_at_period_end && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Expires {new Date(subscriptionData.current_period_end).toLocaleDateString()}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {isProUser ? 'Unlimited access to all features' : 'Limited access with upgrade available'}
            </p>
          </div>
        </div>
      </div>

      {/* Usage Information */}
      <div className="space-y-4">
        {!isProUser ? (
          <>
            {/* Free User Usage Display */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Weekly Sessions</span>
                <span className={`text-sm font-semibold ${
                  hasExceededLimit ? 'text-red-600' : 
                  isApproachingLimit ? 'text-yellow-600' : 'text-gray-900'
                }`}>
                  {weeklyUsage}/{weeklyLimit}
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full transition-all duration-300 ${
                    hasExceededLimit ? 'bg-gradient-to-r from-red-500 to-red-600' :
                    isApproachingLimit ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                    'bg-gradient-to-r from-blue-500 to-cyan-600'
                  }`}
                  style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                ></div>
              </div>
              
              {/* Usage Status Message */}
              <div className={`text-xs ${
                hasExceededLimit ? 'text-red-600' : 
                isApproachingLimit ? 'text-yellow-600' : 'text-gray-600'
              }`}>
                {hasExceededLimit ? (
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Weekly limit reached. Upgrade to Pro for unlimited access.
                  </div>
                ) : isApproachingLimit ? (
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    {weeklyLimit - weeklyUsage} sessions remaining this week
                  </div>
                ) : (
                  `${weeklyLimit - weeklyUsage} sessions remaining this week`
                )}
              </div>

              {/* Reset Information */}
              {usageData?.weekly_usage_reset && (
                <div className="text-xs text-gray-500">
                  Usage resets on {(() => {
                    const resetDate = new Date(usageData.weekly_usage_reset);
                    const nextReset = new Date(resetDate.getTime() + 7 * 24 * 60 * 60 * 1000); // Add 7 days
                    return nextReset.toLocaleDateString();
                  })()}
                </div>
              )}
            </div>

            {/* Contextual Upgrade Prompt */}
            {showUpgradePrompt && (isApproachingLimit || hasExceededLimit) && (
              <ContextualUpgradePrompt
                weeklyUsage={weeklyUsage}
                weeklyLimit={weeklyLimit}
                isProUser={isProUser}
                hasExceededLimit={hasExceededLimit}
                isApproachingLimit={isApproachingLimit}
                onUpgradeClick={onUpgradeClick}
                variant="banner"
                size="sm"
              />
            )}
          </>
        ) : (
          <>
            {/* Pro User Display */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Sessions</span>
                <span className="text-sm font-semibold text-purple-600 flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  Unlimited
                </span>
              </div>
              
              <div className="w-full bg-gradient-to-r from-purple-200 to-pink-200 rounded-full h-2.5">
                <div className="h-2.5 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full w-full"></div>
              </div>
              
              <div className="text-xs text-gray-600">
                Process unlimited resumes with Pro features enabled
              </div>
            </div>

            {/* Pro Features List */}
            <div className="grid grid-cols-2 gap-2 mt-4">
              {[
                { icon: '⚡', label: 'Heavy Tailoring' },
                { icon: '🎨', label: 'Advanced Formatting' },
                { icon: '📊', label: 'Analytics Dashboard' },
                { icon: '💌', label: 'Cover Letters' }
              ].map((feature, index) => (
                <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                  <span className="text-sm">{feature.icon}</span>
                  <span>{feature.label}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Subscription Management Link for Pro Users */}
      {isProUser && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <a 
            href="/subscription"
            className="text-sm text-purple-600 hover:text-purple-700 font-medium transition-colors inline-flex items-center gap-1"
          >
            Manage Subscription 
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      )}
    </div>
  );
};

export default SubscriptionStatus;