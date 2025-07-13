/**
 * API Configuration for production deployment
 * Handles dynamic API URL based on environment
 */

// Get API base URL from environment or fallback to localhost
const getApiBaseUrl = () => {
  // In production, use the environment variable
  if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_ENVIRONMENT === 'production') {
    return process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-domain.railway.app';
  }
  
  // In development, use localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl() + '/api';

// API helper functions
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
};

// Health check function
export const checkBackendHealth = async () => {
  try {
    const response = await fetch(`${getApiBaseUrl()}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Backend health check failed:', error);
    throw error;
  }
};

// Export the base URL for backward compatibility
export default API_BASE_URL; 