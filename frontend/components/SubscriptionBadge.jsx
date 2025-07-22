import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  fetchSubscriptionStatus, 
  formatSubscriptionTier, 
  getUsageStatus,
  getUsagePercentage 
} from '../utils/subscriptionUtils';

const SubscriptionBadge = ({ 
  onClick, 
  showUsage = true, 
  compact = false,
  className = '' 
}) => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSubscriptionData = async () => {
      if (!isAuthenticated || !user) {
        setLoading(false);
        return;
      }

      try {
        const data = await fetchSubscriptionStatus(authenticatedRequest);
        setSubscriptionData(data);
      } catch (error) {
        console.error('Failed to load subscription data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSubscriptionData();

    // Listen for usage updates
    const handleUsageUpdate = () => loadSubscriptionData();
    window.addEventListener('usageUpdated', handleUsageUpdate);
    return () => window.removeEventListener('usageUpdated', handleUsageUpdate);
  }, [isAuthenticated, user, authenticatedRequest]);

  if (!isAuthenticated || loading) {
    return null;
  }

  const isProUser = subscriptionData?.is_pro_active || user?.subscription_tier === 'pro';
  const tierInfo = formatSubscriptionTier(subscriptionData?.subscription_tier || user?.subscription_tier);
  const weeklyUsage = subscriptionData?.weekly_usage_count || user?.weekly_usage_count || 0;
  const weeklyLimit = subscriptionData?.usage_limits?.weekly_sessions || 5;
  const usagePercentage = getUsagePercentage(weeklyUsage, isProUser ? -1 : weeklyLimit);
  const usageStatus = getUsageStatus(weeklyUsage, isProUser ? -1 : weeklyLimit);

  if (compact) {
    return (
      <button
        onClick={onClick}
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 hover:scale-105 ${
          isProUser 
            ? 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 hover:from-purple-200 hover:to-pink-200' 
            : 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800 hover:from-blue-200 hover:to-cyan-200'
        } ${className}`}
      >
        <span className="text-base">{tierInfo.icon}</span>
        <span>{tierInfo.label}</span>
        {!isProUser && showUsage && (
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${
            usageStatus === 'exceeded' ? 'bg-red-100 text-red-700' :
            usageStatus === 'warning' ? 'bg-yellow-100 text-yellow-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {weeklyUsage}/{weeklyLimit}
          </span>
        )}
      </button>
    );
  }

  return (
    <div 
      className={`bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-white/50 p-4 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 ${className}`}
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        {/* Tier Icon */}
        <div className={`p-2 rounded-lg shadow-md ${
          isProUser 
            ? 'bg-gradient-to-r from-purple-500 to-pink-600' 
            : 'bg-gradient-to-r from-blue-500 to-cyan-600'
        }`}>
          <span className="text-white text-lg">{tierInfo.icon}</span>
        </div>

        {/* Tier Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
              isProUser 
                ? 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800' 
                : 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800'
            }`}>
              {tierInfo.label}
            </span>
            {subscriptionData?.cancel_at_period_end && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Expiring
              </span>
            )}
          </div>

          {/* Usage Display */}
          {showUsage && (
            <div className="mt-2">
              {isProUser ? (
                <div className="flex items-center gap-1 text-xs text-gray-600">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <span>Unlimited</span>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600">Weekly</span>
                    <span className={`font-medium ${
                      usageStatus === 'exceeded' ? 'text-red-600' :
                      usageStatus === 'warning' ? 'text-yellow-600' :
                      'text-gray-900'
                    }`}>
                      {weeklyUsage}/{weeklyLimit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full transition-all duration-300 ${
                        usageStatus === 'exceeded' ? 'bg-gradient-to-r from-red-500 to-red-600' :
                        usageStatus === 'warning' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                        'bg-gradient-to-r from-blue-500 to-cyan-600'
                      }`}
                      style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Arrow Icon */}
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  );
};

export default SubscriptionBadge;