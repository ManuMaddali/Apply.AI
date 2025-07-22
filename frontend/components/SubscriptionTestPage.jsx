import React, { useState } from 'react';
import UpgradeModal from './UpgradeModal';
import UpgradeButton, { ProUpgradeButton, CompactUpgradeButton, FeatureUpgradeButton } from './UpgradeButton';
import UpgradePrompt, { UsageLimitPrompt, FeatureBlockedPrompt, BulkProcessingPrompt } from './UpgradePrompt';
import { useSubscription } from '../hooks/useSubscription';

const SubscriptionTestPage = () => {
  const [showModal, setShowModal] = useState(false);
  const { isProUser, weeklyUsage, weeklyLimit } = useSubscription();

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Subscription Components Test
        </h1>
        <p className="text-gray-600">
          Test all subscription-related components and upgrade flows
        </p>
      </div>

      {/* Current Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-3">Current Status</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Pro User:</span> {isProUser ? 'Yes' : 'No'}
          </div>
          <div>
            <span className="font-medium">Weekly Usage:</span> {weeklyUsage}/{weeklyLimit}
          </div>
        </div>
      </div>

      {/* Upgrade Buttons */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Upgrade Buttons</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="space-y-2">
            <h3 className="font-medium">Primary Button</h3>
            <ProUpgradeButton />
          </div>
          
          <div className="space-y-2">
            <h3 className="font-medium">Compact Button</h3>
            <CompactUpgradeButton />
          </div>
          
          <div className="space-y-2">
            <h3 className="font-medium">Feature Button</h3>
            <FeatureUpgradeButton 
              feature="bulk_processing" 
              featureName="Bulk Processing" 
            />
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="font-medium">Custom Button</h3>
          <UpgradeButton variant="outline" size="large">
            <span>✨</span>
            <span>Custom Upgrade Text</span>
          </UpgradeButton>
        </div>
      </div>

      {/* Upgrade Prompts */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Upgrade Prompts</h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">Usage Limit Prompt (Exceeded)</h3>
            <UsageLimitPrompt 
              weeklyUsage={5} 
              weeklyLimit={5} 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Usage Limit Prompt (Warning)</h3>
            <UsageLimitPrompt 
              weeklyUsage={4} 
              weeklyLimit={5} 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Feature Blocked Prompt</h3>
            <FeatureBlockedPrompt 
              feature="advanced_formatting" 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Feature Blocked Prompt (Compact)</h3>
            <FeatureBlockedPrompt 
              feature="analytics" 
              compact={true} 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Bulk Processing Prompt</h3>
            <BulkProcessingPrompt />
          </div>
        </div>
      </div>

      {/* Generic Upgrade Prompts */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Generic Upgrade Prompts</h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">Blocked Status</h3>
            <UpgradePrompt 
              feature="cover_letters" 
              usageStatus="blocked" 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Exceeded Status</h3>
            <UpgradePrompt 
              feature="resume_processing" 
              usageStatus="exceeded" 
            />
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Warning Status</h3>
            <UpgradePrompt 
              feature="resume_processing" 
              usageStatus="warning" 
            />
          </div>
        </div>
      </div>

      {/* Manual Modal Trigger */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Manual Modal</h2>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Open Upgrade Modal
        </button>
      </div>

      {/* Manual Upgrade Modal */}
      <UpgradeModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        feature="test_feature"
      />
    </div>
  );
};

export default SubscriptionTestPage;