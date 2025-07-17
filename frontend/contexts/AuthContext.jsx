import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Token management
  const getToken = () => {
    return localStorage.getItem('applyai_token');
  };

  const setToken = (token) => {
    if (token) {
      localStorage.setItem('applyai_token', token);
    } else {
      localStorage.removeItem('applyai_token');
    }
  };

  // API call with authentication
  const authenticatedRequest = async (url, options = {}) => {
    const token = getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Token expired or invalid
        await logout();
        throw new Error('Authentication required');
      }

      return response;
    } catch (error) {
      if (error.message === 'Authentication required') {
        throw error;
      }
      throw new Error(`Request failed: ${error.message}`);
    }
  };

  // Check authentication status
  const checkAuth = async () => {
    const token = getToken();
    console.log('🔍 [AuthContext] Checking auth, token exists:', !!token);
    
    if (!token) {
      console.log('🔍 [AuthContext] No token found, setting unauthenticated state');
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
      return false;
    }

    // Debug token format
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = parts[1];
        const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
        const decoded = JSON.parse(atob(paddedPayload));
        console.log('🔍 [AuthContext] Token payload:', decoded);
        
        // Check if token is expired
        if (decoded.exp) {
          const expDate = new Date(decoded.exp * 1000);
          const now = new Date();
          console.log('🔍 [AuthContext] Token expires at:', expDate);
          console.log('🔍 [AuthContext] Current time:', now);
          console.log('🔍 [AuthContext] Token expired?', expDate < now);
          
          if (expDate < now) {
            console.log('⚠️ [AuthContext] Token is expired, clearing auth state');
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
            setLoading(false);
            return false;
          }
        }
      }
    } catch (e) {
      console.error('❌ [AuthContext] Failed to decode token:', e);
    }

    try {
      const authUrl = `${API_BASE_URL}/api/auth/me`;
      console.log('🔍 [AuthContext] Making auth check request to:', authUrl);
      console.log('🔍 [AuthContext] Using token:', token.substring(0, 50) + '...');
      
      // Make a direct fetch request instead of using authenticatedRequest
      // This ensures we're using the exact token format expected by the backend
      const response = await fetch(authUrl, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('🔍 [AuthContext] Auth check response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('🔍 [AuthContext] Auth check response data:', data);
        
        if (data.success && data.user) {
          console.log('✅ [AuthContext] Auth check successful, setting user data');
          setUser(data.user);
          setIsAuthenticated(true);
          setError(null);
          return true;
        } else {
          console.log('❌ [AuthContext] Auth check response missing success or user data');
        }
      } else {
        console.log('❌ [AuthContext] Auth check failed with status:', response.status);
        try {
          const errorData = await response.json();
          console.log('❌ [AuthContext] Error response:', errorData);
        } catch (e) {
          const errorText = await response.text();
          console.log('❌ [AuthContext] Error response (text):', errorText);
        }
        
        // Invalid token or failed response
        console.log('🔍 [AuthContext] Auth check failed, clearing token and user data');
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
        return false;
      }
      
      // Invalid token or failed response
      console.log('🔍 [AuthContext] Auth check failed, clearing token and user data');
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      return false;
    } catch (error) {
      console.error('❌ [AuthContext] Auth check error:', error);
      console.error('❌ [AuthContext] Error details:', {
        message: error.message,
        stack: error.stack
      });
      
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setError('Authentication check failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Login with email and password
  const login = async (email, password, rememberMe = false) => {
    setLoading(true);
    setError(null);

    try {
      // Ensure email and password are properly trimmed to avoid whitespace issues
      const trimmedEmail = typeof email === 'string' ? email.trim() : email;
      const trimmedPassword = typeof password === 'string' ? password : password;
      
      // Debug log to see what URL is being used
      const loginUrl = `${API_BASE_URL}/api/auth/login`;
      console.log('Login URL:', loginUrl);
      console.log('API_BASE_URL:', API_BASE_URL);
      console.log('Login payload:', { 
        email: trimmedEmail, 
        password: '********', 
        remember_me: rememberMe,
        email_length: trimmedEmail.length,
        password_length: trimmedPassword.length
      });
      
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: trimmedEmail,
          password: trimmedPassword,
          remember_me: rememberMe,
        }),
      });

      const data = await response.json();
      console.log('Login response status:', response.status);
      console.log('Login response data:', data);

      if (response.ok && data.success) {
        console.log('Setting token and user data');
        setToken(data.access_token);
        setUser(data.user);
        setIsAuthenticated(true);
        setError(null);
        return { success: true, user: data.user };
      } else {
        const errorMessage = data.detail || 'Login failed';
        console.error('Login error:', errorMessage);
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Login exception:', error);
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Register new user
  const register = async (userData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Don't automatically log in - user needs to verify email
        setError(null);
        return { 
          success: true, 
          message: data.message,
          user: data.user 
        };
      } else {
        const errorMessage = data.detail || 'Registration failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Social login
  const socialLogin = async (provider, accessToken, providerData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/social-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider,
          access_token: accessToken,
          ...providerData,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setToken(data.access_token);
        setUser(data.user);
        setIsAuthenticated(true);
        setError(null);
        return { success: true, user: data.user };
      } else {
        const errorMessage = data.detail || 'Social login failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    setLoading(true);
    
    try {
      const token = getToken();
      if (token) {
        // Try to logout on server
        await authenticatedRequest(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
        });
      }
    } catch (error) {
      // Ignore errors during logout
    } finally {
      // Always clear local state
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
      setLoading(false);
    }
  };

  // Password reset
  const requestPasswordReset = async (email) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setError(null);
        return { success: true, message: data.message };
      } else {
        const errorMessage = data.detail || 'Password reset request failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Reset password with token
  const resetPassword = async (token, newPassword) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setError(null);
        return { success: true, message: data.message };
      } else {
        const errorMessage = data.detail || 'Password reset failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Email verification
  const verifyEmail = async (token) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-email?token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setError(null);
        // Refresh user data if authenticated
        if (isAuthenticated) {
          await checkAuth();
        }
        return { success: true, message: data.message };
      } else {
        const errorMessage = data.detail || 'Email verification failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Resend verification email
  const resendVerification = async (email) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/resend-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setError(null);
        return { success: true, message: data.message };
      } else {
        const errorMessage = data.detail || 'Failed to resend verification email';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authenticatedRequest(`${API_BASE_URL}/api/auth/profile`, {
        method: 'PUT',
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setUser(data.user);
        setError(null);
        return { success: true, user: data.user };
      } else {
        const errorMessage = data.detail || 'Profile update failed';
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      const errorMessage = 'Network error. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Helper functions
  const canGenerateResume = () => {
    return user?.can_generate_resume || false;
  };

  const isPremiumUser = () => {
    return user?.is_premium || false;
  };

  const isEmailVerified = () => {
    return user?.email_verified || false;
  };

  const getUserRole = () => {
    return user?.role || 'free';
  };

  const getUsageLimits = () => {
    return user?.usage_limits || {
      resumes_per_month: 3,
      jobs_per_batch: 3,
      cover_letters: false,
      advanced_ai: false,
      priority_support: false
    };
  };

  // Check auth on mount and when token changes
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'applyai_token') {
        console.log('🔄 [AuthContext] Token changed in localStorage, refreshing auth state');
        // Small delay to ensure token is fully written
        setTimeout(() => {
          checkAuth();
        }, 100);
      }
    };

    // Also listen for custom storage events (dispatched manually by OAuth callbacks)
    const handleCustomStorageEvent = (e) => {
      if (e.detail && e.detail.key === 'applyai_token') {
        console.log('🔄 [AuthContext] Custom token change event received');
        setTimeout(() => {
          checkAuth();
        }, 100);
      }
    };

    // Add event listeners for storage changes (helps with OAuth flow)
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('authTokenChanged', handleCustomStorageEvent);
    
    // Initial auth check
    console.log('🔄 [AuthContext] Performing initial auth check...');
    checkAuth();

    // Also check for token periodically in case of OAuth flow
    const tokenCheckInterval = setInterval(() => {
      const token = localStorage.getItem('applyai_token');
      if (token && !isAuthenticated) {
        console.log('🔄 [AuthContext] Found token while unauthenticated, checking auth...');
        checkAuth();
      }
    }, 1000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authTokenChanged', handleCustomStorageEvent);
      clearInterval(tokenCheckInterval);
    };
  }, [isAuthenticated]);

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    socialLogin,
    logout,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    resendVerification,
    updateProfile,
    checkAuth,
    authenticatedRequest,
    getToken,
    
    // Helper functions
    canGenerateResume,
    isPremiumUser,
    isEmailVerified,
    getUserRole,
    getUsageLimits,
    
    // Clear error
    clearError: () => setError(null),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 