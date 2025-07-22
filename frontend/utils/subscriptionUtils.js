import { API_BASE_URL } from './api';

/**
 * Subscription and Usage Utilities
 * Handles subscription status checks, usage tracking, and real-time updates
 */

// Custom event to notify components of usage updates
export const dispatchUsageUpdate = () => {
  const event = new CustomEvent('usageUpdated', {
    detail: { timestamp: new Date().toISOString() }
  });
  window.dispatchEvent(event);
};

// Custom event to notify components of subscription changes
export const dispatchSubscriptionChange = () => {
  const event = new CustomEvent('subscriptionChanged', {
    detail: { timestamp: new Date().toISOString() }
  });
  window.dispatchEvent(event);
};

// Fetch current subscription status
export const fetchSubscriptionStatus = async (authenticatedRequest) => {
  try {
    console.log('🔍 [subscriptionUtils] Fetching subscription status from:', `${API_BASE_URL}/api/subscription/status`);
    const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/status`);
    console.log('🔍 [subscriptionUtils] Subscription status response:', response.status);

    if (response.ok) {
      const data = await response.json();
      console.log('✅ [subscriptionUtils] Subscription status data:', data);
      return data;
    }

    const errorText = await response.text();
    console.error('❌ [subscriptionUtils] Subscription status failed:', response.status, errorText);
    throw new Error(`Failed to fetch subscription status: ${response.status} - ${errorText}`);
  } catch (error) {
    console.error('❌ [subscriptionUtils] Error fetching subscription status:', error);
    throw error;
  }
};

// Fetch usage statistics
export const fetchUsageStatistics = async (authenticatedRequest) => {
  try {
    console.log('🔍 [subscriptionUtils] Fetching usage statistics from:', `${API_BASE_URL}/api/subscription/usage`);
    const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/usage`);
    console.log('🔍 [subscriptionUtils] Usage statistics response:', response.status);

    if (response.ok) {
      const data = await response.json();
      console.log('✅ [subscriptionUtils] Usage statistics data:', data);
      return data;
    }

    const errorText = await response.text();
    console.error('❌ [subscriptionUtils] Usage statistics failed:', response.status, errorText);
    throw new Error(`Failed to fetch usage statistics: ${response.status} - ${errorText}`);
  } catch (error) {
    console.error('❌ [subscriptionUtils] Error fetching usage statistics:', error);
    throw error;
  }
};

// Create subscription upgrade
export const createSubscription = async (authenticatedRequest, paymentMethodId) => {
  try {
    const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/upgrade`, {
      method: 'POST',
      body: JSON.stringify({
        payment_method_id: paymentMethodId
      })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Subscription creation failed');
    }

    return result;
  } catch (error) {
    console.error('Error creating subscription:', error);
    throw error;
  }
};

// Cancel subscription
export const cancelSubscription = async (authenticatedRequest, cancelData = {}) => {
  try {
    const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/cancel`, {
      method: 'POST',
      body: JSON.stringify({
        cancel_immediately: cancelData.cancel_immediately || false,
        reason: cancelData.reason || null
      })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Subscription cancellation failed');
    }

    return result;
  } catch (error) {
    console.error('Error canceling subscription:', error);
    throw error;
  }
};

// Check if user can perform an action based on subscription
export const checkFeatureAccess = (subscriptionData, feature) => {
  if (!subscriptionData) return false;

  const isProActive = subscriptionData.is_pro_active;
  const usageLimits = subscriptionData.usage_limits || {};

  switch (feature) {
    case 'resume_processing':
      if (isProActive) return true;
      const weeklyLimit = usageLimits.weekly_sessions || 5;
      const currentUsage = subscriptionData.weekly_usage_count || 0;
      return currentUsage < weeklyLimit;

    case 'bulk_processing':
      return isProActive;

    case 'cover_letters':
      return isProActive && usageLimits.cover_letters;

    case 'advanced_formatting':
      return isProActive && usageLimits.advanced_formatting;

    case 'heavy_tailoring':
      return isProActive && usageLimits.heavy_tailoring;

    case 'analytics':
      return isProActive && usageLimits.analytics;

    default:
      return false;
  }
};

// Get usage percentage for progress bars
export const getUsagePercentage = (current, limit) => {
  if (limit === -1 || limit === 0) return 0; // Unlimited or no limit
  return Math.min((current / limit) * 100, 100);
};

// Get usage status (normal, warning, exceeded)
export const getUsageStatus = (current, limit) => {
  if (limit === -1) return 'unlimited';
  if (current >= limit) return 'exceeded';
  if (current / limit >= 0.8) return 'warning';
  return 'normal';
};

// Format subscription tier for display
export const formatSubscriptionTier = (tier) => {
  switch (tier?.toLowerCase()) {
    case 'pro':
      return { label: '🚀 Pro', color: 'purple' };
    case 'free':
    default:
      return { label: '🆓 Free', color: 'blue' };
  }
};

// Get upgrade prompt message based on usage
export const getUpgradePromptMessage = (usageStatus, feature) => {
  const messages = {
    exceeded: {
      resume_processing: 'Weekly limit reached! Upgrade to Pro for unlimited resume processing.',
      bulk_processing: 'Bulk processing requires Pro subscription for multiple jobs at once.',
      cover_letters: 'Cover letter generation is a Pro feature.',
      advanced_formatting: 'Advanced formatting options require Pro subscription.',
      heavy_tailoring: 'Heavy tailoring mode is available for Pro users only.',
      analytics: 'Analytics dashboard is a Pro feature.'
    },
    warning: {
      resume_processing: 'You\'re approaching your weekly limit. Consider upgrading to Pro.',
      bulk_processing: 'Process multiple jobs at once with Pro subscription.',
      cover_letters: 'Generate professional cover letters with Pro.',
      advanced_formatting: 'Unlock advanced formatting with Pro.',
      heavy_tailoring: 'Get comprehensive resume optimization with Pro.',
      analytics: 'Track your success with Pro analytics.'
    },
    blocked: {
      resume_processing: 'Resume processing requires an account.',
      bulk_processing: 'Bulk processing is a Pro feature.',
      cover_letters: 'Cover letters are a Pro feature.',
      advanced_formatting: 'Advanced formatting is a Pro feature.',
      heavy_tailoring: 'Heavy tailoring is a Pro feature.',
      analytics: 'Analytics are a Pro feature.'
    }
  };

  return messages[usageStatus]?.[feature] || 'Upgrade to Pro for unlimited access to all features.';
};

// Calculate days until subscription renewal
export const getDaysUntilRenewal = (currentPeriodEnd) => {
  if (!currentPeriodEnd) return null;

  const endDate = new Date(currentPeriodEnd);
  const now = new Date();
  const diffTime = endDate - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return Math.max(0, diffDays);
};

// Format usage reset date
export const formatUsageResetDate = (resetDate) => {
  if (!resetDate) return null;

  const date = new Date(resetDate);
  const now = new Date();
  const diffTime = date - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  if (diffDays < 7) return `In ${diffDays} days`;

  return date.toLocaleDateString();
};

// Subscription status colors and styles
export const getSubscriptionStatusStyles = (tier, status) => {
  const isProActive = tier === 'pro' && status === 'active';

  return {
    badge: {
      className: isProActive
        ? 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800'
        : 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800',
      icon: isProActive ? '🚀' : '🆓',
      label: isProActive ? 'Pro' : 'Free'
    },
    progress: {
      className: isProActive
        ? 'bg-gradient-to-r from-purple-500 to-pink-600'
        : 'bg-gradient-to-r from-blue-500 to-cyan-600'
    },
    container: {
      className: isProActive
        ? 'bg-gradient-to-r from-purple-500 to-pink-600'
        : 'bg-gradient-to-r from-blue-500 to-cyan-600'
    }
  };
};

// Usage tracking for analytics
export const trackUsageEvent = async (authenticatedRequest, eventType, metadata = {}) => {
  try {
    await authenticatedRequest(`${API_BASE_URL}/api/analytics/track`, {
      method: 'POST',
      body: JSON.stringify({
        event_type: eventType,
        metadata: metadata,
        timestamp: new Date().toISOString()
      })
    });
  } catch (error) {
    // Don't throw - analytics tracking shouldn't break the app
    console.warn('Failed to track usage event:', error);
  }
};

// Local storage helpers for caching subscription data
const SUBSCRIPTION_CACHE_KEY = 'applyai_subscription_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const cacheSubscriptionData = (data) => {
  const cacheData = {
    data,
    timestamp: Date.now()
  };
  localStorage.setItem(SUBSCRIPTION_CACHE_KEY, JSON.stringify(cacheData));
};

export const getCachedSubscriptionData = () => {
  try {
    const cached = localStorage.getItem(SUBSCRIPTION_CACHE_KEY);
    if (!cached) return null;

    const { data, timestamp } = JSON.parse(cached);
    const isExpired = Date.now() - timestamp > CACHE_DURATION;

    if (isExpired) {
      localStorage.removeItem(SUBSCRIPTION_CACHE_KEY);
      return null;
    }

    return data;
  } catch (error) {
    localStorage.removeItem(SUBSCRIPTION_CACHE_KEY);
    return null;
  }
};

export const clearSubscriptionCache = () => {
  localStorage.removeItem(SUBSCRIPTION_CACHE_KEY);
};

// Enhanced cancellation function with customer retention
export const cancelSubscriptionWithRetention = async (authenticatedRequest, cancelData = {}) => {
  try {
    // First, try to understand why they're canceling and offer alternatives
    const retentionOffers = {
      'too_expensive': 'Would a 50% discount for 3 months help?',
      'not_using_enough': 'Would you like to pause your subscription instead?',
      'technical_issues': 'Let us help resolve any issues you\'re experiencing',
      'found_alternative': 'What features would make you stay?'
    };

    // This would typically show a retention modal first
    // For now, proceed with cancellation
    return await cancelSubscription(authenticatedRequest, cancelData);
  } catch (error) {
    console.error('Error in retention flow:', error);
    throw error;
  }
};

// Get billing cycle information
export const getBillingCycleInfo = (subscriptionData) => {
  if (!subscriptionData || !subscriptionData.current_period_start || !subscriptionData.current_period_end) {
    return null;
  }

  const start = new Date(subscriptionData.current_period_start);
  const end = new Date(subscriptionData.current_period_end);
  const now = new Date();

  const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
  const daysUsed = Math.ceil((now - start) / (1000 * 60 * 60 * 24));
  const daysRemaining = Math.ceil((end - now) / (1000 * 60 * 60 * 24));

  return {
    start: start.toLocaleDateString(),
    end: end.toLocaleDateString(),
    totalDays,
    daysUsed: Math.max(0, daysUsed),
    daysRemaining: Math.max(0, daysRemaining),
    percentageUsed: Math.min(100, Math.max(0, (daysUsed / totalDays) * 100))
  };
};

// Format currency for display
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase()
  }).format(amount);
};

// Get subscription health status
export const getSubscriptionHealth = (subscriptionData) => {
  if (!subscriptionData) return { status: 'unknown', message: 'No subscription data' };

  const { subscription_status, is_pro_active, cancel_at_period_end } = subscriptionData;

  if (subscription_status === 'active' && is_pro_active && !cancel_at_period_end) {
    return { status: 'healthy', message: 'Your subscription is active and healthy' };
  }

  if (cancel_at_period_end) {
    return { status: 'ending', message: 'Your subscription will end at the current period' };
  }

  if (subscription_status === 'past_due') {
    return { status: 'warning', message: 'Payment is past due - please update your payment method' };
  }

  if (subscription_status === 'canceled') {
    return { status: 'canceled', message: 'Your subscription has been canceled' };
  }

  return { status: 'unknown', message: 'Subscription status unclear' };
};

// Fetch recent batch processing jobs
export const fetchRecentBatchJobs = async (authenticatedRequest) => {
  try {
    const response = await authenticatedRequest(`${API_BASE_URL}/api/batch/list-jobs`);

    if (response.ok) {
      const data = await response.json();
      return data.jobs || [];
    }

    const errorText = await response.text();
    console.error('❌ [subscriptionUtils] Failed to fetch recent batch jobs:', response.status, errorText);
    return [];
  } catch (error) {
    console.error('❌ [subscriptionUtils] Error fetching recent batch jobs:', error);
    return [];
  }
};