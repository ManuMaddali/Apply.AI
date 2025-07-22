import React, { useState } from 'react';
import { useSubscription } from '../hooks/useSubscription';
import UpgradeModal from './UpgradeModal';

const ProBenefitsCard = ({ 
  compact = false, 
  showUpgradeButton = true,
  className = '',
  onUpgradeClick 
}) => {
  const { isProUser } = useSubscription();
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const handleUpgradeClick = () => {
    if (onUpgradeClick) {
      onUpgradeClick();
    } else {
      setShowUpgradeModal(true);
    }
  };

  const benefits = [
    {
      icon: '⚡',
      title: 'Unlimited Processing',
      description: 'Process unlimited resumes without weekly limits',
      free: '5 per week',
      pro: 'Unlimited'
    },
    {
      icon: '📊',
      title: 'Bulk Processing',
      description: 'Process up to 10 job applications simultaneously',
      free: 'Single job only',
      pro: 'Up to 10 jobs'
    },
    {
      icon: '🎯',
      title: 'Heavy Tailoring',
      description: 'Comprehensive resume restructuring and optimization',
      free: 'Light tailoring only',
      pro: 'Light & Heavy modes'
    },
    {
      icon: '🎨',
      title: 'Advanced Formatting',
      description: 'Multiple layout styles and customization options',
      free: 'Standard format',
      pro: 'Multiple styles'
    },
    {
      icon: '💌',
      title: 'Premium Cover Letters',
      description: 'Advanced AI-generated cover letters with premium templates',
      free: 'Basic templates',
      pro: 'Premium templates'
    },
    {
      icon: '📈',
      title: 'Analytics Dashboard',
      description: 'Track success rates and optimization metrics',
      free: 'Not available',
      pro: 'Full analytics'
    }
  ];

  if (compact) {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-purple-800">
                {isProUser ? 'Pro Features Active' : 'Unlock Pro Features'}
              </h3>
              <p className="text-sm text-purple-600">
                {isProUser ? 'All premium features available' : 'Unlimited processing, bulk jobs, and more'}
              </p>
            </div>
          </div>
          
          {!isProUser && showUpgradeButton && (
            <button
              onClick={handleUpgradeClick}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold text-sm transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Upgrade
            </button>
          )}
        </div>
        
        <UpgradeModal
          isOpen={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
        />
      </div>
    );
  }

  return (
    <div className={`bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 ${className}`}>
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          {isProUser ? 'Pro Features Active' : 'Upgrade to Pro'}
        </h2>
        <p className="text-gray-600">
          {isProUser 
            ? 'You have access to all premium features' 
            : 'Unlock unlimited processing and advanced features'
          }
        </p>
      </div>

      {/* Benefits Grid */}
      <div className="space-y-4 mb-6">
        {benefits.map((benefit, index) => (
          <div key={index} className="flex items-start gap-4 p-3 rounded-lg bg-gradient-to-r from-gray-50/50 to-purple-50/30">
            <div className="text-2xl">{benefit.icon}</div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">{benefit.title}</h3>
              <p className="text-sm text-gray-600 mb-2">{benefit.description}</p>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1">
                  <span className="text-gray-500">Free:</span>
                  <span className="text-gray-600 font-medium">{benefit.free}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-purple-600">Pro:</span>
                  <span className="text-purple-700 font-semibold">{benefit.pro}</span>
                </div>
              </div>
            </div>
            {isProUser && (
              <div className="text-green-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pricing and CTA */}
      {!isProUser && (
        <>
          <div className="text-center mb-6 p-4 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl">
            <div className="text-2xl font-bold text-purple-800">$9.99/month</div>
            <div className="text-sm text-purple-600">Cancel anytime • No setup fees</div>
          </div>

          {showUpgradeButton && (
            <button
              onClick={handleUpgradeClick}
              className="w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Upgrade to Pro Now
              </span>
            </button>
          )}
        </>
      )}

      {/* Pro User Management */}
      {isProUser && (
        <div className="text-center">
          <button
            onClick={() => window.location.href = '/subscription'}
            className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 font-medium transition-colors"
          >
            Manage Subscription
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}

      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
      />
    </div>
  );
};

export default ProBenefitsCard;