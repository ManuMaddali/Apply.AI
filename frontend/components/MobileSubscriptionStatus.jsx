import React from 'react';
import { useSubscription } from '../hooks/useSubscription';
import UsageIndicator from './UsageIndicator';
import UpgradePrompt from './UpgradePrompt';

const MobileSubscriptionStatus = ({ onUpgradeClick }) => {
  const { 
    isProUser, 
    hasExceededLimit, 
    isApproachingLimit,
    weeklyUsage,
    weeklyLimit 
  } = useSubscription();

  if (isProUser) {
    return (
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-3 rounded-lg mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🚀</span>
            <span className="font-semibold">Pro</span>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span>Unlimited</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 mb-4">
      {/* Usage Status Bar */}
      <div className={`p-3 rounded-lg border-2 ${
        hasExceededLimit ? 'border-red-300 bg-red-50' :
        isApproachingLimit ? 'border-yellow-300 bg-yellow-50' :
        'border-blue-300 bg-blue-50'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Weekly Sessions</span>
          <span className={`text-sm font-bold ${
            hasExceededLimit ? 'text-red-600' :
            isApproachingLimit ? 'text-yellow-600' :
            'text-blue-600'
          }`}>
            {weeklyUsage}/{weeklyLimit}
          </span>
        </div>
        
        <UsageIndicator 
          compact={false}
          showLabel={false}
          showProgress={true}
        />
        
        {hasExceededLimit && (
          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs text-red-600">Limit reached</span>
            <button
              onClick={onUpgradeClick}
              className="text-xs bg-red-600 text-white px-2 py-1 rounded font-medium"
            >
              Upgrade
            </button>
          </div>
        )}
      </div>

      {/* Upgrade Prompt for approaching limit */}
      {isApproachingLimit && !hasExceededLimit && (
        <UpgradePrompt
          feature="resume_processing"
          usageStatus="warning"
          onUpgradeClick={onUpgradeClick}
          compact={true}
        />
      )}
    </div>
  );
};

export default MobileSubscriptionStatus;