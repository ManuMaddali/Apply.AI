import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../../../contexts/AuthContext';

export default function GoogleCallback() {
  const router = useRouter();
  const { checkAuth } = useAuth();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing Google authentication...');
  const [hasProcessed, setHasProcessed] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Prevent double processing
      if (hasProcessed) return;
      setHasProcessed(true);

      try {
        // Debug logging to help diagnose issues
        console.log('🔍 [GoogleCallback] OAuth callback processing...');
        
        const { code, error, error_description } = router.query;
        
        if (error) {
          console.error('OAuth error:', error, error_description);
          setStatus('error');
          setMessage(error_description || 'Google authentication was denied');
          return;
        }
        
        if (!code) {
          console.error('No OAuth code received');
          setStatus('error');
          setMessage('No authorization code received from Google');
          return;
        }
        
        // Exchange code for tokens via backend
        const redirectUri = "http://localhost:3000/auth/callback/google";
        console.log("🔍 [GoogleCallback] Using redirect URI:", redirectUri);
        console.log("🔍 [GoogleCallback] Exchanging code for token...");
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/oauth/callback/google`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            code: code,
            redirect_uri: redirectUri
          })
        });
        
        const data = await response.json();
        console.log('🔍 [GoogleCallback] OAuth callback response:', data);
        
        if (response.ok && data.success) {
          // Clear any existing auth state first to prevent conflicts
          const { access_token, user } = data;
        
          // Store authentication data
          localStorage.setItem('applyai_token', access_token);
          localStorage.setItem('user', JSON.stringify(user));
          
          // Dispatch custom event to notify AuthContext
          window.dispatchEvent(new CustomEvent('authTokenChanged', { 
            detail: { key: 'applyai_token' } 
          }));
        
          // Update auth context
          if (checkAuth) {
            await checkAuth();
          }
        
          // Small delay to ensure auth context is updated
          setTimeout(() => {
            router.push('/app');
          }, 100);
        } else {
          console.error('OAuth callback failed:', data);
          setStatus('error');
          setMessage(data.detail || 'Google authentication failed');
        }
        
      } catch (error) {
        console.error('🔍 [GoogleCallback] Google callback error:', error);
        setStatus('error');
        setMessage('An error occurred during Google authentication: ' + error.message);
      }
    };
    
    if (router.isReady && !hasProcessed) {
      handleCallback();
    }
  }, [router.isReady, router.query, checkAuth, hasProcessed, router]);

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="h-8 w-8 animate-spin text-blue-600" />;
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-600" />;
      default:
        return <Loader2 className="h-8 w-8 animate-spin text-blue-600" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-blue-600';
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-md w-full bg-white/80 backdrop-blur-sm border border-white/50 shadow-xl rounded-lg p-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Google Authentication
          </h2>
          
          <p className={`text-sm ${getStatusColor()}`}>
            {message}
          </p>
          
          {status === 'error' && (
            <div className="mt-6">
              <button
                onClick={() => router.push('/login')}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Return to Login
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 