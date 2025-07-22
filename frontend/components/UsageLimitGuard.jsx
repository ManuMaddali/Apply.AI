import React, { useState } from 'react';
import { useSubscription, useUsageLimits } from '../hooks/useSubscription';
import UpgradePrompt, { UsageLimitPrompt, BulkProcessingPrompt } from './UpgradePrompt';
import UpgradeModal from './UpgradeModal';

/**
 * UsageLimitGuard - Wraps components and enforces usage limits with appropriate UI feedback
 */
const UsageLimitGuard = ({ 
  children, 
  feature = 'resume_processing',
  showWarnings = true,
  blockWhenExceeded = true,
  className = ''
}) => {
  const { isProUser, canUseFeature } = useSubscription();
  const { 
    usageMessage, 
    shouldShowWarning,
    weeklyUsage,
    weeklyLimit
  } = useUsageLimits();
  
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const canUseThisFeature = canUseFeature(feature);
  const isBlocked = blockWhenExceeded && !canUseThisFeature;

  const handleUpgradeClick = () => {
    setShowUpgradeModal(true);
  };

  const handleDismiss = () => {
    setDismissed(true);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Usage Warning Banner */}
      {showWarnings && shouldShowWarning && !dismissed && !isProUser && (
        <div className="mb-4">
          <UsageLimitPrompt
            weeklyUsage={weeklyUsage}
            weeklyLimit={weeklyLimit}
            onUpgradeClick={handleUpgradeClick}
            onDismiss={handleDismiss}
          />
        </div>
      )}

      {/* Content with overlay if blocked */}
      <div className={`relative ${isBlocked ? 'pointer-events-none' : ''}`}>
        {children}
        
        {/* Blocking Overlay */}
        {isBlocked && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-2xl flex items-center justify-center z-10">
            <div className="text-center p-6 max-w-md">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature === 'resume_processing' ? 'Weekly Limit Reached' : 'Pro Feature Required'}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                {usageMessage}
              </p>
              <button
                onClick={handleUpgradeClick}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Upgrade to Pro - $9.99/month
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        feature={feature}
      />
    </div>
  );
};

/**
 * BulkProcessingGuard - Specifically for bulk processing restrictions
 */
export const BulkProcessingGuard = ({ 
  children, 
  jobCount = 0,
  onUpgradeClick,
  className = ''
}) => {
  const { isProUser } = useSubscription();
  const [dismissed, setDismissed] = useState(false);

  // Show bulk processing prompt if user has multiple jobs but isn't Pro
  const shouldShowBulkPrompt = !isProUser && jobCount > 1 && !dismissed;
  const shouldRestrictToBulk = !isProUser && jobCount > 1;

  const handleUpgradeClick = () => {
    if (onUpgradeClick) {
      onUpgradeClick();
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Bulk Processing Promotion */}
      {shouldShowBulkPrompt && (
        <div className="mb-4">
          <BulkProcessingPrompt
            onUpgradeClick={handleUpgradeClick}
            onDismiss={() => setDismissed(true)}
          />
        </div>
      )}

      {/* Content with restriction notice */}
      <div className="relative">
        {children}
        
        {/* Single Job Restriction Notice */}
        {shouldRestrictToBulk && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-yellow-800">
                  Free Plan Limitation
                </h4>
                <p className="text-sm text-yellow-700 mt-1">
                  You&apos;ve added {jobCount} job URLs, but Free users can only process one job at a time. 
                  Only the first job will be processed, or upgrade to Pro for bulk processing.
                </p>
                <button
                  onClick={handleUpgradeClick}
                  className="mt-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-semibold transition-all duration-200"
                >
                  Upgrade for Bulk Processing
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * FeatureGuard - Generic guard for Pro-only features
 */
export const FeatureGuard = ({ 
  children, 
  feature,
  fallback = null,
  showUpgradePrompt = true,
  compact = false,
  className = ''
}) => {
  const { canUseFeature } = useSubscription();
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const canUse = canUseFeature(feature);

  if (!canUse) {
    if (fallback) {
      return fallback;
    }

    if (showUpgradePrompt) {
      return (
        <div className={className}>
          <UpgradePrompt
            feature={feature}
            usageStatus="blocked"
            onUpgradeClick={() => setShowUpgradeModal(true)}
            compact={compact}
          />
          <UpgradeModal
            isOpen={showUpgradeModal}
            onClose={() => setShowUpgradeModal(false)}
            feature={feature}
          />
        </div>
      );
    }

    return null;
  }

  return <div className={className}>{children}</div>;
};

/**
 * UsageWarningBanner - Standalone warning banner for usage limits
 */
export const UsageWarningBanner = ({ 
  onUpgradeClick,
  onDismiss,
  className = ''
}) => {
  const { 
    shouldShowWarning, 
    weeklyUsage, 
    weeklyLimit,
    isProUser 
  } = useUsageLimits();

  if (isProUser || !shouldShowWarning) {
    return null;
  }

  return (
    <div className={`mb-4 ${className}`}>
      <UsageLimitPrompt
        weeklyUsage={weeklyUsage}
        weeklyLimit={weeklyLimit}
        onUpgradeClick={onUpgradeClick}
        onDismiss={onDismiss}
      />
    </div>
  );
};

export default UsageLimitGuard;