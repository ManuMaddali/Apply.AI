import React, { useState } from 'react';
import { getUpgradePromptMessage } from '../utils/subscriptionUtils';
import UpgradeModal from './UpgradeModal';

const UpgradePrompt = ({ 
  feature, 
  usageStatus = 'blocked', 
  onUpgradeClick,
  onDismiss,
  compact = false,
  showDismiss = true,
  className = ''
}) => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const message = getUpgradePromptMessage(usageStatus, feature);

  const handleUpgradeClick = () => {
    if (onUpgradeClick) {
      onUpgradeClick();
    } else {
      setShowUpgradeModal(true);
    }
  };
  
  const getPromptStyles = () => {
    switch (usageStatus) {
      case 'exceeded':
        return {
          container: 'border-red-300 bg-red-50',
          text: 'text-red-800',
          subtext: 'text-red-600',
          button: 'bg-red-600 hover:bg-red-700 text-white',
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        };
      case 'warning':
        return {
          container: 'border-yellow-300 bg-yellow-50',
          text: 'text-yellow-800',
          subtext: 'text-yellow-600',
          button: 'bg-yellow-600 hover:bg-yellow-700 text-white',
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          )
        };
      case 'blocked':
      default:
        return {
          container: 'border-blue-300 bg-blue-50',
          text: 'text-blue-800',
          subtext: 'text-blue-600',
          button: 'bg-blue-600 hover:bg-blue-700 text-white',
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          )
        };
    }
  };

  const styles = getPromptStyles();

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border-2 border-dashed ${styles.container} ${className}`}>
        <div className={styles.text}>
          {styles.icon}
        </div>
        <span className={`text-sm font-medium ${styles.text}`}>
          {feature === 'resume_processing' && usageStatus === 'exceeded' ? 'Limit reached!' : 'Pro Feature'}
        </span>
        <button
          onClick={handleUpgradeClick}
          className={`px-3 py-1 rounded text-xs font-semibold transition-all duration-200 ${styles.button}`}
        >
          Upgrade
        </button>
        {showDismiss && onDismiss && (
          <button
            onClick={onDismiss}
            className={`p-1 rounded hover:bg-black/10 ${styles.text}`}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`p-4 rounded-xl border-2 border-dashed ${styles.container} ${className}`}>
      <div className="flex items-start gap-3">
        <div className={styles.text}>
          {styles.icon}
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className={`text-sm font-semibold ${styles.text}`}>
              {usageStatus === 'exceeded' ? 'Usage Limit Reached' :
               usageStatus === 'warning' ? 'Approaching Limit' :
               'Pro Feature Required'}
            </h4>
            {showDismiss && onDismiss && (
              <button
                onClick={onDismiss}
                className={`p-1 rounded hover:bg-black/10 ${styles.text}`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          
          <p className={`text-sm mt-1 ${styles.subtext}`}>
            {message}
          </p>
          
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={handleUpgradeClick}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 shadow-lg hover:shadow-xl ${styles.button}`}
            >
              Upgrade to Pro - $9.99/month
            </button>
            
            {/* Feature highlights */}
            <div className="hidden sm:flex items-center gap-4 text-xs text-gray-600">
              <div className="flex items-center gap-1">
                <span>⚡</span>
                <span>Unlimited</span>
              </div>
              <div className="flex items-center gap-1">
                <span>🎨</span>
                <span>Advanced</span>
              </div>
              <div className="flex items-center gap-1">
                <span>📊</span>
                <span>Analytics</span>
              </div>
            </div>
          </div>
        </div>
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

// Specific upgrade prompts for common scenarios
export const UsageLimitPrompt = ({ weeklyUsage, weeklyLimit, onUpgradeClick, onDismiss }) => {
  const remaining = weeklyLimit - weeklyUsage;
  const isExceeded = remaining <= 0;
  const isWarning = remaining <= 1;
  
  return (
    <UpgradePrompt
      feature="resume_processing"
      usageStatus={isExceeded ? 'exceeded' : isWarning ? 'warning' : 'normal'}
      onUpgradeClick={onUpgradeClick}
      onDismiss={onDismiss}
    />
  );
};

export const FeatureBlockedPrompt = ({ feature, onUpgradeClick, onDismiss, compact = false }) => {
  return (
    <UpgradePrompt
      feature={feature}
      usageStatus="blocked"
      onUpgradeClick={onUpgradeClick}
      onDismiss={onDismiss}
      compact={compact}
    />
  );
};

export const BulkProcessingPrompt = ({ onUpgradeClick, onDismiss }) => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const handleUpgradeClick = () => {
    if (onUpgradeClick) {
      onUpgradeClick();
    } else {
      setShowUpgradeModal(true);
    }
  };

  return (
    <>
      <div className="p-6 rounded-xl border-2 border-dashed border-purple-300 bg-purple-50">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-100 rounded-lg">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-purple-800">
                Bulk Processing Available
              </h3>
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="p-1 rounded hover:bg-purple-200 text-purple-600"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            
            <p className="text-purple-600 mt-2">
              Process up to 10 job applications simultaneously with Pro subscription. 
              Save time and apply to more positions efficiently.
            </p>
            
            <div className="flex items-center gap-4 mt-4">
              <button
                onClick={handleUpgradeClick}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Upgrade to Pro - $9.99/month
              </button>
              
              <div className="flex items-center gap-4 text-sm text-purple-600">
                <div className="flex items-center gap-1">
                  <span>📊</span>
                  <span>Up to 10 jobs</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>⚡</span>
                  <span>Parallel processing</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>💌</span>
                  <span>Cover letters included</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        feature="bulk_processing"
      />
    </>
  );
};

export default UpgradePrompt;