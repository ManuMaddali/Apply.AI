import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../utils/api';
import {
  fetchSubscriptionStatus,
  cancelSubscription,
  formatSubscriptionTier,
  getDaysUntilRenewal,
  getBillingCycleInfo,
  getSubscriptionHealth
} from '../utils/subscriptionUtils';
import RetentionModal from './RetentionModal';

// Overview Tab Component
const OverviewTab = ({ subscriptionData, isProUser }) => {
  const billingCycle = getBillingCycleInfo(subscriptionData);
  const subscriptionHealth = getSubscriptionHealth(subscriptionData);

  return (
    <div className="space-y-6">
      {/* Subscription Health Alert */}
      {subscriptionHealth.status !== 'healthy' && subscriptionHealth.status !== 'unknown' && (
        <div className={`rounded-xl p-4 ${subscriptionHealth.status === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
          subscriptionHealth.status === 'ending' ? 'bg-blue-50 border border-blue-200' :
            'bg-red-50 border border-red-200'
          }`}>
          <div className="flex items-center">
            <svg className={`w-5 h-5 mr-2 ${subscriptionHealth.status === 'warning' ? 'text-yellow-600' :
              subscriptionHealth.status === 'ending' ? 'text-blue-600' :
                'text-red-600'
              }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className={`font-medium ${subscriptionHealth.status === 'warning' ? 'text-yellow-800' :
              subscriptionHealth.status === 'ending' ? 'text-blue-800' :
                'text-red-800'
              }`}>
              {subscriptionHealth.message}
            </span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Plan</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Plan:</span>
              <span className="font-medium">{isProUser ? 'Pro' : 'Free'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="font-medium capitalize">{subscriptionData?.subscription_status}</span>
            </div>
            {isProUser && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Billing Cycle:</span>
                  <span className="font-medium">Monthly</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Next Billing:</span>
                  <span className="font-medium">
                    {subscriptionData?.current_period_end ?
                      new Date(subscriptionData.current_period_end).toLocaleDateString() :
                      'N/A'
                    }
                  </span>
                </div>
                {billingCycle && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Billing Period Progress</span>
                      <span className="font-medium">{Math.round(billingCycle.percentageUsed)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${billingCycle.percentageUsed}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{billingCycle.daysUsed} days used</span>
                      <span>{billingCycle.daysRemaining} days remaining</span>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Features</h3>
          <div className="space-y-2">
            {(isProUser ? [
              { feature: 'Unlimited Resume Processing', available: true },
              { feature: 'Heavy Tailoring Mode', available: true },
              { feature: 'Advanced Formatting', available: true },
              { feature: 'Premium Cover Letters', available: true },
              { feature: 'Analytics Dashboard', available: true },
              { feature: 'Bulk Processing', available: true }
            ] : [
              { feature: 'Resume Processing', available: true, limit: '5/week' },
              { feature: 'Light Tailoring Mode', available: true },
              { feature: 'Standard Formatting', available: true },
              { feature: 'Basic Cover Letters', available: false },
              { feature: 'Analytics Dashboard', available: false },
              { feature: 'Bulk Processing', available: false }
            ]).map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-600">{item.feature}</span>
                <div className="flex items-center">
                  {item.limit && <span className="text-sm text-gray-500 mr-2">{item.limit}</span>}
                  {item.available ? (
                    <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Billing History Tab Component
const BillingHistoryTab = ({ billingHistory, onDownloadReceipt }) => (
  <div>
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Billing History</h3>
    {billingHistory.length === 0 ? (
      <div className="text-center py-8">
        <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-gray-500">No billing history available</p>
      </div>
    ) : (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Receipt</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {billingHistory.map((payment) => (
              <tr key={payment.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(payment.payment_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {payment.description || 'Subscription Payment'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${payment.amount_dollars.toFixed(2)} {payment.currency.toUpperCase()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${payment.status === 'succeeded'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                    }`}>
                    {payment.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {payment.downloadable ? (
                    <button
                      onClick={() => onDownloadReceipt(payment.stripe_invoice_id)}
                      className="text-indigo-600 hover:text-indigo-900 font-medium"
                    >
                      Download
                    </button>
                  ) : (
                    <span className="text-gray-400">N/A</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}
  </div>
);

// Payment Methods Tab Component
const PaymentMethodsTab = ({ paymentMethods, onRefresh }) => (
  <div>
    <div className="flex justify-between items-center mb-4">
      <h3 className="text-lg font-semibold text-gray-900">Payment Methods</h3>
      <button
        onClick={onRefresh}
        className="px-4 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-300 hover:border-indigo-400 rounded-lg transition-colors"
      >
        Add Payment Method
      </button>
    </div>
    {paymentMethods.length === 0 ? (
      <div className="text-center py-8">
        <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
        <p className="text-gray-500">No payment methods saved</p>
      </div>
    ) : (
      <div className="space-y-4">
        {paymentMethods.map((method) => (
          <div key={method.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-10 h-6 bg-gray-200 rounded mr-3 flex items-center justify-center">
                  <span className="text-xs font-medium">{method.card?.brand?.toUpperCase()}</span>
                </div>
                <div>
                  <p className="font-medium">•••• •••• •••• {method.card?.last4}</p>
                  <p className="text-sm text-gray-500">Expires {method.card?.exp_month}/{method.card?.exp_year}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {method.is_default && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                    Default
                  </span>
                )}
                <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

// Analytics Tab Component
const AnalyticsTab = ({ analyticsData }) => (
  <div>
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics Dashboard</h3>
    {!analyticsData ? (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Loading analytics data...</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white">
          <h4 className="text-lg font-semibold mb-2">Success Rate</h4>
          <p className="text-3xl font-bold">{analyticsData.success_rate || '0'}%</p>
          <p className="text-blue-100 text-sm">Based on your applications</p>
        </div>
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white">
          <h4 className="text-lg font-semibold mb-2">Keyword Score</h4>
          <p className="text-3xl font-bold">{analyticsData.keyword_score || '0'}/100</p>
          <p className="text-green-100 text-sm">Average optimization</p>
        </div>
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white">
          <h4 className="text-lg font-semibold mb-2">Resumes Created</h4>
          <p className="text-3xl font-bold">{analyticsData.total_resumes || '0'}</p>
          <p className="text-purple-100 text-sm">This month</p>
        </div>
      </div>
    )}
  </div>
);

// Cancel Subscription Modal Component
const CancelSubscriptionModal = ({ onCancel, onConfirm, reason, onReasonChange }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Cancel Subscription</h3>
      <p className="text-gray-600 mb-4">
        We're sorry to see you go! Your Pro features will remain active until the end of your current billing period.
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Help us improve - why are you canceling? (optional)
        </label>
        <textarea
          value={reason}
          onChange={(e) => onReasonChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          rows={3}
          placeholder="Your feedback helps us improve..."
        />
      </div>

      <div className="flex space-x-3">
        <button
          onClick={onCancel}
          className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Keep Subscription
        </button>
        <button
          onClick={onConfirm}
          className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          Cancel Subscription
        </button>
      </div>
    </div>
  </div>
);

const SubscriptionDashboard = () => {
  const { user, isAuthenticated, authenticatedRequest } = useAuth();
  const [loading, setLoading] = useState(true);
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRetentionModal, setShowRetentionModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');

  useEffect(() => {
    if (isAuthenticated && user) {
      loadDashboardData();
    }
  }, [isAuthenticated, user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load subscription status
      const statusData = await fetchSubscriptionStatus(authenticatedRequest);
      setSubscriptionData(statusData);

      // Load billing history
      const billingResponse = await authenticatedRequest(`${API_BASE_URL}/api/subscription/billing-history`);
      if (billingResponse.ok) {
        const billingData = await billingResponse.json();
        setBillingHistory(billingData.billing_history || []);
      }

      // Load payment methods
      const paymentResponse = await authenticatedRequest(`${API_BASE_URL}/api/subscription/payment-methods`);
      if (paymentResponse.ok) {
        const paymentData = await paymentResponse.json();
        setPaymentMethods(paymentData.payment_methods || []);
      }

      // Load analytics for Pro users
      if (statusData?.is_pro_active) {
        const analyticsResponse = await authenticatedRequest(`${API_BASE_URL}/api/subscription/analytics-dashboard`);
        if (analyticsResponse.ok) {
          const analytics = await analyticsResponse.json();
          setAnalyticsData(analytics);
        }
      }

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load subscription information');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    try {
      const result = await cancelSubscription(authenticatedRequest, {
        cancel_immediately: false,
        reason: cancelReason
      });

      if (result.success) {
        setShowCancelModal(false);
        setCancelReason('');
        await loadDashboardData(); // Refresh data
      } else {
        setError(result.message || 'Failed to cancel subscription');
      }
    } catch (err) {
      setError('Failed to cancel subscription');
    }
  };

  const downloadReceipt = async (invoiceId) => {
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/receipt/${invoiceId}`);
      if (response.ok) {
        const receiptData = await response.json();
        window.open(receiptData.receipt_url, '_blank');
      }
    } catch (err) {
      console.error('Error downloading receipt:', err);
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Please log in to view your subscription</h2>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const isProUser = subscriptionData?.is_pro_active;
  const tierInfo = formatSubscriptionTier(subscriptionData?.subscription_tier);
  const daysUntilRenewal = subscriptionData?.current_period_end ?
    getDaysUntilRenewal(subscriptionData.current_period_end) : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Subscription Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage your subscription, billing, and account settings</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Subscription Overview Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-white/50 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-lg ${isProUser
                ? 'bg-gradient-to-r from-purple-500 to-pink-600'
                : 'bg-gradient-to-r from-blue-500 to-cyan-600'
                }`}>
                {isProUser ? (
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                ) : (
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                )}
              </div>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-semibold ${isProUser
                    ? 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800'
                    : 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800'
                    }`}>
                    {tierInfo.icon} {tierInfo.label}
                  </span>
                  {subscriptionData?.cancel_at_period_end && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                      Expires {new Date(subscriptionData.current_period_end).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <p className="text-gray-600">
                  {isProUser ? 'Unlimited access to all premium features' : 'Limited access with upgrade available'}
                </p>
                {isProUser && daysUntilRenewal !== null && (
                  <p className="text-sm text-gray-500 mt-1">
                    {daysUntilRenewal === 0 ? 'Renews today' :
                      daysUntilRenewal === 1 ? 'Renews tomorrow' :
                        `Renews in ${daysUntilRenewal} days`}
                  </p>
                )}
              </div>
            </div>
            {isProUser && !subscriptionData?.cancel_at_period_end && (
              <button
                onClick={() => setShowRetentionModal(true)}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 border border-red-300 hover:border-red-400 rounded-lg transition-colors"
              >
                Cancel Subscription
              </button>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-2xl shadow-lg border border-white/50 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'overview', label: 'Overview', icon: '📊' },
                { id: 'billing', label: 'Billing History', icon: '💳' },
                { id: 'payment', label: 'Payment Methods', icon: '💰' },
                ...(isProUser ? [{ id: 'analytics', label: 'Analytics', icon: '📈' }] : [])
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <OverviewTab
                subscriptionData={subscriptionData}
                isProUser={isProUser}
              />
            )}
            {activeTab === 'billing' && (
              <BillingHistoryTab
                billingHistory={billingHistory}
                onDownloadReceipt={downloadReceipt}
              />
            )}
            {activeTab === 'payment' && (
              <PaymentMethodsTab
                paymentMethods={paymentMethods}
                onRefresh={loadDashboardData}
              />
            )}
            {activeTab === 'analytics' && isProUser && (
              <AnalyticsTab analyticsData={analyticsData} />
            )}
          </div>
        </div>

        {/* Retention Modal */}
        {showRetentionModal && (
          <RetentionModal
            isOpen={showRetentionModal}
            onClose={() => setShowRetentionModal(false)}
            onProceedWithCancel={() => {
              setShowRetentionModal(false);
              setShowCancelModal(true);
            }}
            onRetentionOfferAccepted={(offer) => {
              console.log('Retention offer accepted:', offer);
              // Handle retention offer acceptance
              setShowRetentionModal(false);
            }}
            cancelReason={cancelReason}
          />
        )}

        {/* Cancel Subscription Modal */}
        {showCancelModal && (
          <CancelSubscriptionModal
            onCancel={() => setShowCancelModal(false)}
            onConfirm={handleCancelSubscription}
            reason={cancelReason}
            onReasonChange={setCancelReason}
          />
        )}
      </div>
    </div>
  );
};

export default SubscriptionDashboard;