import React, { useState } from 'react';

const RetentionModal = ({ 
  isOpen, 
  onClose, 
  onProceedWithCancel, 
  onRetentionOfferAccepted,
  cancelReason 
}) => {
  const [selectedOffer, setSelectedOffer] = useState(null);
  const [showFinalConfirm, setShowFinalConfirm] = useState(false);

  if (!isOpen) return null;

  // Determine retention offers based on cancel reason
  const getRetentionOffers = (reason) => {
    const offers = {
      'too_expensive': [
        {
          id: 'discount_50',
          title: '50% Off for 3 Months',
          description: 'Continue with Pro features at half price',
          value: '$4.99/month for 3 months, then $9.99/month',
          highlight: true
        },
        {
          id: 'pause_subscription',
          title: 'Pause Your Subscription',
          description: 'Take a break and resume anytime',
          value: 'Pause for up to 3 months'
        }
      ],
      'not_using_enough': [
        {
          id: 'usage_coaching',
          title: 'Free Usage Coaching',
          description: 'Let us help you get more value from Pro features',
          value: '30-minute consultation call'
        },
        {
          id: 'feature_tutorial',
          title: 'Personalized Tutorial',
          description: 'Learn advanced features you might have missed',
          value: 'Custom walkthrough session'
        }
      ],
      'technical_issues': [
        {
          id: 'priority_support',
          title: 'Priority Technical Support',
          description: 'Direct line to our technical team',
          value: 'Immediate issue resolution'
        },
        {
          id: 'account_review',
          title: 'Account Health Check',
          description: 'Full review of your account setup',
          value: 'Comprehensive technical audit'
        }
      ],
      'found_alternative': [
        {
          id: 'feature_request',
          title: 'Custom Feature Development',
          description: 'Tell us what features would make you stay',
          value: 'Priority feature development'
        },
        {
          id: 'competitor_match',
          title: 'Feature Matching',
          description: 'We\'ll match competitor features you need',
          value: 'Custom solution development'
        }
      ],
      'default': [
        {
          id: 'discount_25',
          title: '25% Off Next 6 Months',
          description: 'Continue with a significant discount',
          value: '$7.49/month for 6 months',
          highlight: true
        },
        {
          id: 'extended_trial',
          title: 'Extended Pro Trial',
          description: 'Extra time to explore all features',
          value: '30 additional days free'
        }
      ]
    };

    return offers[reason] || offers['default'];
  };

  const retentionOffers = getRetentionOffers(cancelReason);

  const handleOfferSelect = (offer) => {
    setSelectedOffer(offer);
  };

  const handleAcceptOffer = () => {
    if (selectedOffer) {
      onRetentionOfferAccepted(selectedOffer);
      onClose();
    }
  };

  const handleProceedWithCancel = () => {
    if (showFinalConfirm) {
      onProceedWithCancel();
      onClose();
    } else {
      setShowFinalConfirm(true);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {!showFinalConfirm ? (
          <>
            {/* Retention Offers */}
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Wait! Don't Go Yet 🎯</h3>
              <p className="text-gray-600">
                We'd love to keep you as a Pro user. Here are some special offers just for you:
              </p>
            </div>

            <div className="space-y-4 mb-6">
              {retentionOffers.map((offer) => (
                <div
                  key={offer.id}
                  onClick={() => handleOfferSelect(offer)}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    selectedOffer?.id === offer.id
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${offer.highlight ? 'ring-2 ring-yellow-400 ring-opacity-50' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{offer.title}</h4>
                        {offer.highlight && (
                          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                            Most Popular
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm mb-2">{offer.description}</p>
                      <p className="text-indigo-600 font-medium text-sm">{offer.value}</p>
                    </div>
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      selectedOffer?.id === offer.id
                        ? 'border-indigo-500 bg-indigo-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedOffer?.id === offer.id && (
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleProceedWithCancel}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                No Thanks, Cancel Anyway
              </button>
              <button
                onClick={handleAcceptOffer}
                disabled={!selectedOffer}
                className={`flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  selectedOffer
                    ? 'text-white bg-indigo-600 hover:bg-indigo-700'
                    : 'text-gray-400 bg-gray-200 cursor-not-allowed'
                }`}
              >
                Accept This Offer
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Final Confirmation */}
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Final Confirmation</h3>
              <p className="text-gray-600 mb-4">
                Are you absolutely sure you want to cancel your Pro subscription?
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-yellow-800 mb-2">You'll lose access to:</h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• Unlimited resume processing</li>
                  <li>• Heavy tailoring mode</li>
                  <li>• Advanced formatting options</li>
                  <li>• Premium cover letter templates</li>
                  <li>• Analytics dashboard</li>
                  <li>• Bulk processing capabilities</li>
                </ul>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowFinalConfirm(false)}
                className="flex-1 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
              >
                Keep My Subscription
              </button>
              <button
                onClick={handleProceedWithCancel}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
              >
                Yes, Cancel Subscription
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RetentionModal;