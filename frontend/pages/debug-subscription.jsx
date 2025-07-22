import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../hooks/useSubscription';
import { API_BASE_URL } from '../utils/api';

export default function DebugSubscription() {
  const { user, isAuthenticated, authenticatedRequest, getToken } = useAuth();
  const { subscriptionData, usageData, loading, error } = useSubscription();
  const [testResults, setTestResults] = useState({});

  const testEndpoints = async () => {
    const token = getToken();
    console.log('Token exists:', !!token);
    console.log('Token preview:', token ? token.substring(0, 50) + '...' : 'None');
    
    const results = {};
    
    // Test subscription status
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/status`);
      if (response.ok) {
        const data = await response.json();
        results.subscriptionStatus = { success: true, data };
      } else {
        results.subscriptionStatus = { success: false, error: `${response.status}: ${response.statusText}` };
      }
    } catch (error) {
      results.subscriptionStatus = { success: false, error: error.message };
    }
    
    // Test usage statistics
    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/subscription/usage`);
      if (response.ok) {
        const data = await response.json();
        results.usageStats = { success: true, data };
      } else {
        results.usageStats = { success: false, error: `${response.status}: ${response.statusText}` };
      }
    } catch (error) {
      results.usageStats = { success: false, error: error.message };
    }
    
    setTestResults(results);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Subscription Debug Page</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Auth Status */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
            <div className="space-y-2">
              <p><strong>Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
              <p><strong>User:</strong> {user?.email || 'None'}</p>
              <p><strong>Token exists:</strong> {getToken() ? '✅ Yes' : '❌ No'}</p>
              <p><strong>API Base URL:</strong> {API_BASE_URL}</p>
            </div>
          </div>
          
          {/* Subscription Hook Data */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">useSubscription Hook</h2>
            <div className="space-y-2">
              <p><strong>Loading:</strong> {loading ? '⏳ Yes' : '✅ No'}</p>
              <p><strong>Error:</strong> {error || '✅ None'}</p>
              <p><strong>Subscription Data:</strong> {subscriptionData ? '✅ Loaded' : '❌ None'}</p>
              <p><strong>Usage Data:</strong> {usageData ? '✅ Loaded' : '❌ None'}</p>
            </div>
          </div>
          
          {/* Subscription Data Details */}
          {subscriptionData && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Subscription Details</h2>
              <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto">
                {JSON.stringify(subscriptionData, null, 2)}
              </pre>
            </div>
          )}
          
          {/* Usage Data Details */}
          {usageData && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Usage Details</h2>
              <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto">
                {JSON.stringify(usageData, null, 2)}
              </pre>
            </div>
          )}
          
          {/* Manual Test */}
          <div className="bg-white p-6 rounded-lg shadow col-span-full">
            <h2 className="text-xl font-semibold mb-4">Manual API Test</h2>
            <button 
              onClick={testEndpoints}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Test API Endpoints
            </button>
            
            {Object.keys(testResults).length > 0 && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Test Results:</h3>
                <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto">
                  {JSON.stringify(testResults, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}