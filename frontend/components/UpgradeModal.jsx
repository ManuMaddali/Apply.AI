import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../utils/api';
import { dispatchSubscriptionChange } from '../utils/subscriptionUtils';

// Initialize Stripe
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

// Card element styling
const cardElementOptions = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
      fontFamily: 'system-ui, -apple-system, sans-serif',
    },
    invalid: {
      color: '#9e2146',
    },
  },
  hidePostalCode: false,
};

// Payment form component
const PaymentForm = ({ onSuccess, onError, loading, setLoading }) => {
  const stripe = useStripe();
  const elements = useElements();
  const { authenticatedRequest, user } = useAuth();
  const [cardError, setCardError] = useState(null);
  const [cardComplete, setCardComplete] = useState(false);
  const [processing, setProcessing] = useState(false);

  const handleCardChange = (event) => {
    setCardError(event.error ? event.error.message : null);
    setCardComplete(event.complete);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements || processing) {
      return;
    }

    if (!cardComplete) {
      setCardError('Please complete your card information');
      return;
    }

    setProcessing(true);
    setLoading(true);
    setCardError(null);

    try {
      // Create payment method
      const cardElement = elements.getElement(CardElement);
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
        billing_details: {
          name: user?.full_name || user?.email,
          email: user?.email,
        },
      });

      if (paymentMethodError) {
        throw new Error(paymentMethodError.message);
      }

      // Create subscription on backend
      const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/upgrade`, {
        method: 'POST',
        body: JSON.stringify({
          payment_method_id: paymentMethod.id,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Payment failed');
      }

      // Handle 3D Secure authentication if required
      if (result.requires_action) {
        const { error: confirmError } = await stripe.confirmCardPayment(
          result.payment_intent_client_secret
        );

        if (confirmError) {
          throw new Error(confirmError.message);
        }

        // Payment succeeded after authentication
        onSuccess(result);
      } else if (result.success) {
        // Payment succeeded immediately
        onSuccess(result);
      } else {
        throw new Error('Payment processing failed');
      }
    } catch (error) {
      console.error('Payment error:', error);
      setCardError(error.message);
      onError(error.message);
    } finally {
      setProcessing(false);
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border border-gray-300 rounded-lg bg-white">
        <CardElement
          options={cardElementOptions}
          onChange={handleCardChange}
        />
      </div>
      
      {cardError && (
        <div className="text-red-600 text-sm flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {cardError}
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || !cardComplete || processing || loading}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 ${
          !stripe || !cardComplete || processing || loading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl'
        }`}
      >
        {processing || loading ? (
          <div className="flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Processing...
          </div>
        ) : (
          'Subscribe to Pro - $9.99/month'
        )}
      </button>
    </form>
  );
};

// Feature comparison component
const FeatureComparison = () => {
  const features = [
    {
      name: 'Resume Processing',
      free: '5 per week',
      pro: 'Unlimited',
      icon: '📄'
    },
    {
      name: 'Bulk Processing',
      free: 'Single job only',
      pro: 'Up to 10 jobs',
      icon: '📊'
    },
    {
      name: 'Tailoring Mode',
      free: 'Light only',
      pro: 'Light & Heavy',
      icon: '⚡'
    },
    {
      name: 'Advanced Formatting',
      free: 'Standard only',
      pro: 'Multiple styles',
      icon: '🎨'
    },
    {
      name: 'Cover Letters',
      free: 'Basic templates',
      pro: 'Premium templates',
      icon: '💌'
    },
    {
      name: 'Analytics Dashboard',
      free: '❌',
      pro: '✅',
      icon: '📈'
    }
  ];

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
        Feature Comparison
      </h3>
      
      <div className="space-y-3">
        {features.map((feature, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">{feature.icon}</span>
              <span className="text-sm font-medium text-gray-700">
                {feature.name}
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-xs">
              <div className="text-center">
                <div className="text-gray-500 font-medium">Free</div>
                <div className="text-gray-600">{feature.free}</div>
              </div>
              
              <div className="text-center">
                <div className="text-purple-600 font-medium">Pro</div>
                <div className="text-purple-700 font-semibold">{feature.pro}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Success confirmation component
const SuccessConfirmation = ({ onClose }) => {
  return (
    <div className="text-center py-6">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Welcome to Pro! 🚀
      </h3>
      
      <p className="text-gray-600 mb-6">
        Your subscription is now active. You have immediate access to all Pro features.
      </p>
      
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 mb-6">
        <h4 className="font-semibold text-purple-800 mb-2">What&apos;s unlocked:</h4>
        <div className="grid grid-cols-2 gap-2 text-sm text-purple-700">
          <div className="flex items-center gap-1">
            <span>⚡</span>
            <span>Unlimited processing</span>
          </div>
          <div className="flex items-center gap-1">
            <span>📊</span>
            <span>Bulk processing</span>
          </div>
          <div className="flex items-center gap-1">
            <span>🎨</span>
            <span>Advanced formatting</span>
          </div>
          <div className="flex items-center gap-1">
            <span>📈</span>
            <span>Analytics dashboard</span>
          </div>
        </div>
      </div>
      
      <button
        onClick={onClose}
        className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
      >
        Start Using Pro Features
      </button>
    </div>
  );
};

// Main upgrade modal component
const UpgradeModal = ({ isOpen, onClose, feature = null }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setError(null);
      setSuccess(false);
      setLoading(false);
    }
  }, [isOpen]);

  const handleSuccess = (result) => {
    console.log('Payment successful:', result);
    setSuccess(true);
    setError(null);
    
    // Dispatch event to update subscription status across the app
    dispatchSubscriptionChange();
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setSuccess(false);
  };

  const handleClose = () => {
    if (success) {
      // Reload page to refresh subscription status
      window.location.reload();
    } else {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {success ? 'Subscription Confirmed' : 'Upgrade to Pro'}
              </h2>
              {!success && (
                <p className="text-sm text-gray-600 mt-1">
                  {feature ? `Unlock ${feature} and more` : 'Unlock all premium features'}
                </p>
              )}
            </div>
            
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={loading}
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {success ? (
            <SuccessConfirmation onClose={handleClose} />
          ) : (
            <>
              {/* Pricing */}
              <div className="text-center mb-6">
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-4">
                  <div className="text-3xl font-bold text-purple-800">$9.99</div>
                  <div className="text-sm text-purple-600">per month</div>
                  <div className="text-xs text-purple-500 mt-1">Cancel anytime</div>
                </div>
                
                <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <span>Secure payment with Stripe</span>
                </div>
              </div>

              {/* Feature comparison toggle */}
              <div className="mb-6">
                <button
                  onClick={() => setShowComparison(!showComparison)}
                  className="w-full text-left text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center justify-between"
                >
                  <span>Compare Free vs Pro features</span>
                  <svg 
                    className={`w-4 h-4 transition-transform ${showComparison ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {showComparison && (
                  <div className="mt-3">
                    <FeatureComparison />
                  </div>
                )}
              </div>

              {/* Error display */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center gap-2 text-red-800">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium">Payment Failed</span>
                  </div>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              )}

              {/* Payment form */}
              <Elements stripe={stripePromise}>
                <PaymentForm
                  onSuccess={handleSuccess}
                  onError={handleError}
                  loading={loading}
                  setLoading={setLoading}
                />
              </Elements>

              {/* Terms */}
              <div className="mt-4 text-xs text-gray-500 text-center">
                By subscribing, you agree to our{' '}
                <span className="text-purple-600 hover:underline cursor-pointer">Terms of Service</span>
                {' '}and{' '}
                <span className="text-purple-600 hover:underline cursor-pointer">Privacy Policy</span>.
                You can cancel your subscription at any time.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UpgradeModal;