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

export const API_BASE_URL = getApiBaseUrl();

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

/**
 * Download file from API endpoint
 * Handles PDF, RTF, DOCX and other file types with proper blob handling
 * 
 * @param {string} endpoint - The API endpoint to download from (e.g., '/download/batch123/file.pdf')
 * @param {string} filename - Optional custom filename for download. If not provided, extracts from endpoint
 * @param {object} options - Optional fetch options (headers, auth tokens, etc.)
 * @returns {Promise<void>} - Resolves when download starts, rejects on error
 */
export const downloadFile = async (endpoint, filename = null, options = {}) => {
  let objectUrl = null;
  
  try {
    // Build full URL
    const url = `${API_BASE_URL}${endpoint}`;
    
    console.log(`📥 Starting download from: ${url}`);
    
    // Fetch the file
    const response = await fetch(url, {
      method: 'GET',
      ...options,
      headers: {
        // Don't set Content-Type for download requests
        ...options.headers,
      },
    });
    
    // Check if request was successful
    if (!response.ok) {
      let errorMessage = `Download failed: ${response.status} ${response.statusText}`;
      
      // Try to parse error message from response
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        }
      } catch (e) {
        // Use default error message if parsing fails
      }
      
      throw new Error(errorMessage);
    }
    
    // Get content type and disposition from headers
    const contentType = response.headers.get('content-type') || 'application/octet-stream';
    const contentDisposition = response.headers.get('content-disposition');
    
    // Extract filename from content-disposition header if available
    if (!filename && contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '');
      }
    }
    
    // If still no filename, extract from endpoint
    if (!filename) {
      const pathParts = endpoint.split('/');
      filename = pathParts[pathParts.length - 1] || 'download';
      
      // Add appropriate extension based on content type if missing
      if (!filename.includes('.')) {
        const extensionMap = {
          'application/pdf': '.pdf',
          'application/rtf': '.rtf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
          'application/msword': '.doc',
          'text/plain': '.txt',
          'text/html': '.html',
        };
        
        const extension = extensionMap[contentType] || '';
        filename += extension;
      }
    }
    
    // Convert response to blob
    const blob = await response.blob();
    
    // Validate blob
    if (!blob || blob.size === 0) {
      throw new Error('Downloaded file is empty');
    }
    
    console.log(`📦 File size: ${(blob.size / 1024).toFixed(2)} KB`);
    
    // Create object URL from blob
    objectUrl = window.URL.createObjectURL(blob);
    
    // Create temporary anchor element
    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = filename;
    link.style.display = 'none';
    
    // Add to document, click, and remove
    document.body.appendChild(link);
    
    // Trigger download
    link.click();
    
    // Clean up DOM
    document.body.removeChild(link);
    
    // Clean up object URL after a short delay to ensure download starts
    setTimeout(() => {
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
        console.log(`✅ Successfully downloaded: ${filename}`);
      }
    }, 100);
    
    return { success: true, filename, size: blob.size };
    
  } catch (error) {
    // Clean up object URL if it was created
    if (objectUrl) {
      window.URL.revokeObjectURL(objectUrl);
    }
    
    console.error('❌ Download failed:', error);
    
    // Provide user-friendly error messages
    let userMessage = 'Failed to download file. ';
    
    if (error.message.includes('404')) {
      userMessage += 'The file was not found.';
    } else if (error.message.includes('403')) {
      userMessage += 'You do not have permission to download this file.';
    } else if (error.message.includes('500')) {
      userMessage += 'Server error occurred. Please try again later.';
    } else if (error.message.includes('network')) {
      userMessage += 'Network error. Please check your internet connection.';
    } else {
      userMessage += error.message;
    }
    
    throw new Error(userMessage);
  }
};

/**
 * Download multiple files as a zip archive
 * 
 * @param {string} endpoint - The API endpoint that returns a zip file
 * @param {string} filename - Filename for the downloaded zip
 * @returns {Promise<void>}
 */
export const downloadZip = async (endpoint, filename = 'download.zip') => {
  return downloadFile(endpoint, filename, {
    headers: {
      'Accept': 'application/zip, application/x-zip-compressed',
    },
  });
};

/**
 * Download batch file helper - specifically for batch processing downloads
 * 
 * @param {string} batchId - The batch ID
 * @param {string} filename - The filename to download
 * @returns {Promise<void>}
 */
export const downloadBatchFile = async (batchId, filename) => {
  const endpoint = `/enhanced-batch/download/${batchId}/${filename}`;
  return downloadFile(endpoint, filename);
};

/**
 * Download all batch files as zip
 * 
 * @param {string} batchId - The batch ID
 * @returns {Promise<void>}
 */
export const downloadAllBatchFiles = async (batchId) => {
  const endpoint = `/enhanced-batch/download-all/${batchId}`;
  const filename = `batch_${batchId}_all_files.zip`;
  return downloadZip(endpoint, filename);
}; 