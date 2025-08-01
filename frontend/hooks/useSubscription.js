import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  fetchSubscriptionStatus, 
  fetchUsageStatistics,
  checkFeatureAccess,
  dispatchUsageUpdate,
  cacheSubscriptionData,
  getCachedSubscriptionData,
  clearSubscriptionCache
} from '../utils/subscriptionUtils';

/**
 * Custom hook for managing subscription data and real-time updates
 */
export const useSubscription = () => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load subscription data
  const loadSubscriptionData = useCallback(async (useCache = true) => {
    if (!isAuthenticated || !user) {
      setLoading(false);
      return;
    }

    try {
      setError(null);

      // Try to use cached data first
      if (useCache) {
        const cached = getCachedSubscriptionData();
        if (cached) {
          setSubscriptionData(cached.subscription);
          setUsageData(cached.usage);
          setLoading(false);
          return; // Don't fetch fresh data to reduce API calls
        }
      }

      setLoading(true);

      // Fetch fresh data
      const [subscriptionResponse, usageResponse] = await Promise.all([
        fetchSubscriptionStatus(authenticatedRequest),
        fetchUsageStatistics(authenticatedRequest)
      ]);

      setSubscriptionData(subscriptionResponse);
      setUsageData(usageResponse);

      // Cache the data
      cacheSubscriptionData({
        subscription: subscriptionResponse,
        usage: usageResponse
      });

    } catch (err) {
      console.error('❌ [useSubscription] Error loading subscription data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, authenticatedRequest]);

  // Initial load
  useEffect(() => {
    loadSubscriptionData();
  }, [loadSubscriptionData]);

  // Listen for usage updates and subscription changes (with debouncing)
  useEffect(() => {
    let updateTimeout;
    
    const handleUsageUpdate = () => {
      // Debounce updates to prevent excessive API calls
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(() => {
        loadSubscriptionData(false);
      }, 2000); // Wait 2 seconds before updating
    };

    const handleSubscriptionChange = () => {
      clearSubscriptionCache();
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(() => {
        loadSubscriptionData(false);
      }, 1000);
    };

    window.addEventListener('usageUpdated', handleUsageUpdate);
    window.addEventListener('subscriptionChanged', handleSubscriptionChange);
    
    return () => {
      clearTimeout(updateTimeout);
      window.removeEventListener('usageUpdated', handleUsageUpdate);
      window.removeEventListener('subscriptionChanged', handleSubscriptionChange);
    };
  }, [loadSubscriptionData]);

  // Clear cache when user changes
  useEffect(() => {
    clearSubscriptionCache();
  }, [user?.id]);

  // Helper functions
  const canUseFeature = useCallback((feature) => {
    return checkFeatureAccess(subscriptionData, feature);
  }, [subscriptionData]);

  const isProUser = subscriptionData?.is_pro_active || user?.subscription_tier === 'pro';
  const weeklyUsage = usageData?.weekly_usage_count || user?.weekly_usage_count || 0;
  const weeklyLimit = subscriptionData?.usage_limits?.weekly_sessions || 5;
  const hasExceededLimit = !isProUser && weeklyUsage >= weeklyLimit;
  const isApproachingLimit = !isProUser && weeklyUsage >= weeklyLimit * 0.8;

  // Usage tracking function
  const trackUsage = useCallback(async () => {
    try {
      // Optimistically update local state
      if (usageData) {
        setUsageData(prev => ({
          ...prev,
          weekly_usage_count: (prev.weekly_usage_count || 0) + 1,
          total_usage_count: (prev.total_usage_count || 0) + 1
        }));
      }

      // Dispatch update event for other components (this will trigger debounced refresh)
      dispatchUsageUpdate();

    } catch (error) {
      console.error('Error tracking usage:', error);
    }
  }, [usageData]);

  return {
    // Data
    subscriptionData,
    usageData,
    loading,
    error,
    
    // Status
    isProUser,
    weeklyUsage,
    weeklyLimit,
    hasExceededLimit,
    isApproachingLimit,
    
    // Functions
    canUseFeature,
    trackUsage,
    refreshData: () => loadSubscriptionData(false),
    
    // Computed values
    usagePercentage: isProUser ? 0 : Math.min((weeklyUsage / weeklyLimit) * 100, 100),
    remainingSessions: isProUser ? -1 : Math.max(0, weeklyLimit - weeklyUsage)
  };
};

/**
 * Hook for checking specific feature access
 */
export const useFeatureAccess = (feature) => {
  const { canUseFeature, isProUser, loading } = useSubscription();
  
  return {
    canUse: canUseFeature(feature),
    isProUser,
    loading,
    requiresUpgrade: !canUseFeature(feature) && !loading
  };
};

/**
 * Hook for usage limits and warnings
 */
export const useUsageLimits = () => {
  const { 
    weeklyUsage, 
    weeklyLimit, 
    hasExceededLimit, 
    isApproachingLimit,
    isProUser,
    usagePercentage,
    remainingSessions
  } = useSubscription();

  const getUsageStatus = () => {
    if (isProUser) return 'unlimited';
    if (hasExceededLimit) return 'exceeded';
    if (isApproachingLimit) return 'warning';
    return 'normal';
  };

  const getUsageMessage = () => {
    if (isProUser) return 'Unlimited sessions available';
    if (hasExceededLimit) return 'Weekly limit reached. Upgrade to Pro for unlimited access.';
    if (isApproachingLimit) return `Only ${remainingSessions} sessions remaining this week.`;
    return `${remainingSessions} sessions remaining this week.`;
  };

  return {
    weeklyUsage,
    weeklyLimit,
    remainingSessions,
    usagePercentage,
    usageStatus: getUsageStatus(),
    usageMessage: getUsageMessage(),
    canProcess: isProUser || !hasExceededLimit,
    shouldShowWarning: isApproachingLimit || hasExceededLimit
  };
};

export default useSubscription;