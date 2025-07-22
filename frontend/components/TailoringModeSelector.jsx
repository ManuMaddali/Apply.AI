import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../hooks/useSubscription';
import { API_BASE_URL } from '../utils/api';

const TailoringModeSelector = ({ 
  selectedMode, 
  onModeChange, 
  disabled = false,
  className = "" 
}) => {
  const { user, authenticatedRequest } = useAuth();
  const { isProUser } = useSubscription();
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);

  // Load user's preferred tailoring mode from localStorage or user preferences
  useEffect(() => {
    if (isProUser && user?.preferred_tailoring_mode && !selectedMode) {
      onModeChange(user.preferred_tailoring_mode);
    } else if (!selectedMode) {
      // Default to light mode for free users or when no preference is set
      onModeChange('light');
    }
  }, [isProUser, user, selectedMode, onModeChange]);

  // Save user preference to backend and localStorage when mode changes
  const savePreference = async (mode) => {
    if (!isProUser) return;
    
    try {
      await authenticatedRequest(`${API_BASE_URL}/api/subscription/preferences`, {
        method: 'PUT',
        body: JSON.stringify({
          default_tailoring_mode: mode
        })
      });
      
      // Also save to localStorage as backup
      localStorage.setItem('preferred_tailoring_mode', mode);
    } catch (error) {
      console.warn('Failed to save tailoring mode preference:', error);
      // Still save to localStorage as fallback
      localStorage.setItem('preferred_tailoring_mode', mode);
    }
  };

  const handleModeChange = (mode) => {
    if (!isProUser && mode === 'heavy') {
      setShowUpgradePrompt(true);
      return;
    }
    
    onModeChange(mode);
    
    // Save preference for future sessions
    if (isProUser) {
      savePreference(mode);
    }
  };

  // Don't render for non-Pro users unless showing upgrade prompt
  if (!isProUser && !showUpgradePrompt) {
    return null;
  }

  const modes = [
    {
      id: 'light',
      name: 'Light Tailoring',
      description: 'Quick keyword optimization and targeted changes',
      processingTime: '~30 seconds',
      features: [
        'Keyword optimization',
        'Targeted skill matching',
        'Basic content adjustments',
        'ATS-friendly formatting'
      ],
      icon: '⚡',
      available: true
    },
    {
      id: 'heavy',
      name: 'Heavy Tailoring',
      description: 'Comprehensive restructuring and content optimization',
      processingTime: '~60-90 seconds',
      features: [
        'Complete content restructuring',
        'Advanced skill analysis',
        'Industry-specific optimization',
        'Enhanced achievement highlighting',
        'Deep contextual matching'
      ],
      icon: '🚀',
      available: isProUser,
      proOnly: true
    }
  ];

  return (
    <div className={`bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Tailoring Intensity</h3>
            <p className="text-sm text-gray-600">Choose how deeply to customize your resume</p>
          </div>
        </div>
        {isProUser && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800">
            🚀 Pro Feature
          </span>
        )}
      </div>

      <div className="space-y-4">
        {modes.map((mode) => (
          <div key={mode.id} className="relative">
            <label 
              className={`block cursor-pointer transition-all duration-200 ${
                !mode.available ? 'cursor-not-allowed opacity-60' : ''
              }`}
            >
              <input
                type="radio"
                name="tailoring-mode"
                value={mode.id}
                checked={selectedMode === mode.id}
                onChange={() => handleModeChange(mode.id)}
                disabled={disabled || !mode.available}
                className="sr-only"
              />
              <div className={`relative p-4 rounded-xl border-2 transition-all duration-200 ${
                selectedMode === mode.id
                  ? mode.id === 'heavy' 
                    ? 'border-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 shadow-lg'
                    : 'border-blue-500 bg-gradient-to-r from-blue-50 to-cyan-50 shadow-lg'
                  : 'border-gray-200 bg-white/50 hover:border-gray-300 hover:bg-white/70'
              } ${!mode.available ? 'bg-gray-50' : ''}`}>
                
                {/* Selection indicator */}
                {selectedMode === mode.id && (
                  <div className={`absolute top-3 right-3 w-5 h-5 rounded-full flex items-center justify-center ${
                    mode.id === 'heavy' 
                      ? 'bg-gradient-to-r from-purple-500 to-pink-600'
                      : 'bg-gradient-to-r from-blue-500 to-cyan-600'
                  }`}>
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}

                {/* Pro badge for heavy mode */}
                {mode.proOnly && !isProUser && (
                  <div className="absolute top-3 right-3">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-800">
                      Pro Only
                    </span>
                  </div>
                )}

                <div className="flex items-start gap-4">
                  <div className="text-2xl">{mode.icon}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="text-lg font-semibold text-gray-900">{mode.name}</h4>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        mode.id === 'heavy' 
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {mode.processingTime}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{mode.description}</p>
                    
                    {/* Features list */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                      {mode.features.map((feature, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                          <div className={`w-1.5 h-1.5 rounded-full ${
                            mode.id === 'heavy' 
                              ? 'bg-purple-400'
                              : 'bg-blue-400'
                          }`}></div>
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </label>
          </div>
        ))}
      </div>

      {/* Current selection indicator */}
      {selectedMode && (
        <div className="mt-4 p-3 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              selectedMode === 'heavy' ? 'bg-purple-500' : 'bg-blue-500'
            }`}></div>
            <span className="font-medium text-gray-700">
              Selected: {modes.find(m => m.id === selectedMode)?.name}
            </span>
            {selectedMode === 'heavy' && (
              <span className="text-purple-600 text-xs">
                • Enhanced processing time for better results
              </span>
            )}
          </div>
        </div>
      )}

      {/* Upgrade prompt modal */}
      {showUpgradePrompt && !isProUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Heavy Tailoring is Pro Only</h3>
              <p className="text-gray-600">
                Unlock comprehensive resume optimization with advanced AI analysis and industry-specific customization.
              </p>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Complete content restructuring</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Advanced skill analysis & matching</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Industry-specific optimization</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowUpgradePrompt(false)}
                className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Maybe Later
              </button>
              <button
                onClick={() => {
                  setShowUpgradePrompt(false);
                  window.open('/pricing', '_blank');
                }}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200 font-semibold"
              >
                Upgrade to Pro
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TailoringModeSelector;