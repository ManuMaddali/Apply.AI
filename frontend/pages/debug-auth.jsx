import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function DebugAuth() {
  const { checkAuth, isAuthenticated, user, loading } = useAuth();
  const [debugInfo, setDebugInfo] = useState({});
  const [manualTokenCheck, setManualTokenCheck] = useState(null);

  useEffect(() => {
    const updateDebugInfo = () => {
      const token = localStorage.getItem('applyai_token');
      const userStr = localStorage.getItem('applyai_user');
      
      let tokenDecoded = null;
      if (token) {
        try {
          const parts = token.split('.');
          if (parts.length === 3) {
            const payload = parts[1];
            const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
            tokenDecoded = JSON.parse(atob(paddedPayload));
          }
        } catch (e) {
          tokenDecoded = { error: e.message };
        }
      }

      setDebugInfo({
        tokenExists: !!token,
        tokenLength: token ? token.length : 0,
        tokenDecoded,
        userExists: !!userStr,
        userParsed: userStr ? JSON.parse(userStr) : null,
        authContextState: {
          isAuthenticated,
          user,
          loading
        },
        timestamp: new Date().toISOString()
      });
    };

    updateDebugInfo();
    const interval = setInterval(updateDebugInfo, 1000);
    return () => clearInterval(interval);
  }, [isAuthenticated, user, loading]);

  const handleManualTokenCheck = async () => {
    const token = localStorage.getItem('applyai_token');
    if (!token) {
      setManualTokenCheck({ error: 'No token found' });
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setManualTokenCheck({
        status: response.status,
        ok: response.ok,
        data
      });
    } catch (error) {
      setManualTokenCheck({ error: error.message });
    }
  };

  const handleAuthContextCheck = async () => {
    try {
      const result = await checkAuth();
      console.log('Manual checkAuth result:', result);
    } catch (error) {
      console.error('Manual checkAuth error:', error);
    }
  };

  const clearAllStorage = () => {
    localStorage.removeItem('applyai_token');
    localStorage.removeItem('applyai_user');
    localStorage.removeItem('oauth_return_url');
    sessionStorage.removeItem('oauth_redirect_in_progress');
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Auth Debug Page</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          {/* localStorage Debug */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">localStorage State</h2>
            <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto">
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
          </div>

          {/* Manual Token Check */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Manual Token Check</h2>
            <button 
              onClick={handleManualTokenCheck}
              className="bg-blue-500 text-white px-4 py-2 rounded mb-4 mr-2"
            >
              Test Token with Backend
            </button>
            <button 
              onClick={handleAuthContextCheck}
              className="bg-green-500 text-white px-4 py-2 rounded mb-4 mr-2"
            >
              Trigger AuthContext Check
            </button>
            <button 
              onClick={clearAllStorage}
              className="bg-red-500 text-white px-4 py-2 rounded mb-4"
            >
              Clear All Storage
            </button>
            
            {manualTokenCheck && (
              <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto">
                {JSON.stringify(manualTokenCheck, null, 2)}
              </pre>
            )}
          </div>

          {/* OAuth Test */}
          <div className="bg-white p-6 rounded-lg shadow col-span-full">
            <h2 className="text-xl font-semibold mb-4">OAuth Test Links</h2>
            <p className="mb-4 text-gray-600">
              Click these to test OAuth flow. Watch the console and this debug page.
            </p>
            <div className="space-x-4">
              <a 
                href="http://localhost:8000/api/auth/oauth/google"
                className="bg-red-500 text-white px-4 py-2 rounded inline-block"
              >
                Test Google OAuth
              </a>
              <a 
                href="http://localhost:8000/api/auth/oauth/github"
                className="bg-gray-800 text-white px-4 py-2 rounded inline-block"
              >
                Test GitHub OAuth
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 