import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

const ProtectedRoute = ({ children, requireVerification = false, requirePremium = false }) => {
  const { isAuthenticated, user, loading, checkAuth } = useAuth();
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const performAuthCheck = async () => {
      // If we're already authenticated, mark as checked
      if (isAuthenticated && user) {
        setAuthChecked(true);
        return;
      }

      // If still loading, wait
      if (loading) {
        return;
      }

      // Check if we have a token but no auth state (common after OAuth)
      const token = localStorage.getItem('applyai_token');
      
      if (token && !isAuthenticated) {
        console.log('🔄 [ProtectedRoute] Token exists but not authenticated, checking auth...');
        
        try {
          const success = await checkAuth();
          console.log(`🔄 [ProtectedRoute] Auth check result: ${success ? 'success' : 'failed'}`);
          
          if (success) {
            setAuthChecked(true);
            return;
          }
        } catch (error) {
          console.error('🔄 [ProtectedRoute] Auth check error:', error);
        }
      }
      
      // Mark as checked and handle unauthenticated state
      setAuthChecked(true);
      
      if (!isAuthenticated) {
        // Store the current path to redirect back after login
        const returnUrl = router.asPath;
        console.log(`🔄 [ProtectedRoute] Not authenticated, redirecting to login with returnUrl=${returnUrl}`);
        
        // Clear any OAuth flags
        sessionStorage.removeItem('oauth_redirect_in_progress');
        
        router.push(`/login?returnUrl=${encodeURIComponent(returnUrl)}`);
        return;
      }

      if (requireVerification && user && !user.email_verified) {
        router.push('/verify-email');
        return;
      }

      if (requirePremium && user && !user.is_premium) {
        router.push('/pricing');
        return;
      }
    };
    
    performAuthCheck();
  }, [isAuthenticated, user, loading, router, requireVerification, requirePremium, checkAuth]);

  // Show loading spinner while checking authentication
  if (loading || !authChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  // Don't render if email verification is required but not verified
  if (requireVerification && user && !user.email_verified) {
    return null;
  }

  // Don't render if premium is required but user is not premium
  if (requirePremium && user && !user.is_premium) {
    return null;
  }

  return children;
};

export default ProtectedRoute; 