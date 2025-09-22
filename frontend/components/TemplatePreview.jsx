import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiRequest } from '../utils/api';

const TemplatePreview = ({ 
  templateId, 
  resumeData = null, 
  className = '',
  showControls = true,
  onError = null,
  onLoad = null
}) => {
  // State management
  const [previewHtml, setPreviewHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // Refs
  const iframeRef = useRef(null);
  const containerRef = useRef(null);
  const fullscreenRef = useRef(null);
  const loadTimeoutRef = useRef(null);

  // Constants
  const MAX_RETRIES = 3;
  const LOAD_TIMEOUT = 30000; // 30 seconds
  const MIN_ZOOM = 25;
  const MAX_ZOOM = 200;
  const ZOOM_STEP = 25;

  // Generate cache key for preview
  const getCacheKey = useCallback(() => {
    const dataHash = resumeData ? 
      btoa(JSON.stringify(resumeData)).slice(0, 10) : 'default';
    return `${templateId}-${dataHash}`;
  }, [templateId, resumeData]);

  // Fetch preview from API
  const fetchPreview = useCallback(async (retryAttempt = 0) => {
    if (!templateId) {
      setError('No template selected');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Clear any existing timeout
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }

      // Set a timeout for the request
      loadTimeoutRef.current = setTimeout(() => {
        setError('Preview generation timed out. Please try again.');
        setLoading(false);
      }, LOAD_TIMEOUT);

      let response;

      if (resumeData) {
        // Use POST endpoint for custom data
        response = await apiRequest('/api/templates/preview/' + templateId, {
          method: 'POST',
          body: JSON.stringify({
            resume_data: resumeData,
            format: 'html'
          })
        });
      } else {
        // Use GET endpoint for sample data
        response = await apiRequest(
          `/api/templates/preview/${templateId}?format=html&use_sample=true&cache=true`
        );
      }

      // Clear timeout on successful response
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
        loadTimeoutRef.current = null;
      }

      if (response) {
        // If response is a string (HTML), use it directly
        // If response is an object, extract the HTML
        const htmlContent = typeof response === 'string' ? response : response.html || response.data;
        
        if (htmlContent) {
          setPreviewHtml(htmlContent);
          setRetryCount(0);
          onLoad && onLoad(templateId);
        } else {
          throw new Error('No preview content received');
        }
      } else {
        throw new Error('Empty response from server');
      }

    } catch (err) {
      console.error('Preview fetch error:', err);
      
      // Clear timeout on error
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
        loadTimeoutRef.current = null;
      }

      const errorMessage = err.message || 'Failed to load preview';
      setError(errorMessage);
      onError && onError(errorMessage, templateId);

      // Auto-retry logic
      if (retryAttempt < MAX_RETRIES) {
        console.log(`Retrying preview fetch (${retryAttempt + 1}/${MAX_RETRIES})`);
        setTimeout(() => {
          setRetryCount(retryAttempt + 1);
          fetchPreview(retryAttempt + 1);
        }, 1000 * (retryAttempt + 1)); // Exponential backoff
      }
    } finally {
      setLoading(false);
    }
  }, [templateId, resumeData, onError, onLoad]);

  // Handle iframe load event
  const handleIframeLoad = useCallback(() => {
    if (iframeRef.current && previewHtml) {
      try {
        const iframeDoc = iframeRef.current.contentDocument || iframeRef.current.contentWindow.document;
        
        // Add responsive meta tag for better mobile display
        const metaViewport = iframeDoc.createElement('meta');
        metaViewport.name = 'viewport';
        metaViewport.content = 'width=device-width, initial-scale=1.0';
        iframeDoc.head.appendChild(metaViewport);

        // Add zoom styles
        const zoomStyle = iframeDoc.createElement('style');
        zoomStyle.textContent = `
          body {
            transform: scale(${zoom / 100});
            transform-origin: top left;
            width: ${10000 / zoom}%;
            overflow-x: ${zoom > 100 ? 'auto' : 'hidden'};
          }
          html {
            overflow-x: ${zoom > 100 ? 'auto' : 'hidden'};
          }
        `;
        iframeDoc.head.appendChild(zoomStyle);

      } catch (err) {
        console.warn('Could not access iframe content:', err);
      }
    }
  }, [previewHtml, zoom]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + ZOOM_STEP, MAX_ZOOM));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - ZOOM_STEP, MIN_ZOOM));
  }, []);

  const handleZoomReset = useCallback(() => {
    setZoom(100);
  }, []);

  const handleZoomFit = useCallback(() => {
    if (containerRef.current && iframeRef.current) {
      const containerWidth = containerRef.current.clientWidth;
      const iframeWidth = 800; // Approximate resume width
      const fitZoom = Math.floor((containerWidth / iframeWidth) * 100);
      setZoom(Math.max(Math.min(fitZoom, MAX_ZOOM), MIN_ZOOM));
    }
  }, []);

  // Fullscreen controls
  const toggleFullscreen = useCallback(() => {
    if (!isFullscreen) {
      if (fullscreenRef.current?.requestFullscreen) {
        fullscreenRef.current.requestFullscreen();
      } else if (fullscreenRef.current?.webkitRequestFullscreen) {
        fullscreenRef.current.webkitRequestFullscreen();
      } else if (fullscreenRef.current?.mozRequestFullScreen) {
        fullscreenRef.current.mozRequestFullScreen();
      } else if (fullscreenRef.current?.msRequestFullscreen) {
        fullscreenRef.current.msRequestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      setIsFullscreen(false);
    }
  }, [isFullscreen]);

  // Handle fullscreen change events
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
      );
      setIsFullscreen(isCurrentlyFullscreen);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (isFullscreen) {
        switch (e.key) {
          case 'Escape':
            toggleFullscreen();
            break;
          case '+':
          case '=':
            e.preventDefault();
            handleZoomIn();
            break;
          case '-':
            e.preventDefault();
            handleZoomOut();
            break;
          case '0':
            e.preventDefault();
            handleZoomReset();
            break;
          case 'f':
          case 'F':
            e.preventDefault();
            handleZoomFit();
            break;
        }
      }
    };

    if (isFullscreen) {
      window.addEventListener('keydown', handleKeyPress);
      return () => window.removeEventListener('keydown', handleKeyPress);
    }
  }, [isFullscreen, handleZoomIn, handleZoomOut, handleZoomReset, handleZoomFit, toggleFullscreen]);

  // Fetch preview when template or data changes
  useEffect(() => {
    if (templateId) {
      fetchPreview();
    }
  }, [fetchPreview]);

  // Update iframe when HTML or zoom changes
  useEffect(() => {
    if (iframeRef.current && previewHtml) {
      const iframeDoc = iframeRef.current.contentDocument || iframeRef.current.contentWindow.document;
      iframeDoc.open();
      iframeDoc.write(previewHtml);
      iframeDoc.close();
      
      // Wait for iframe to load then apply zoom
      setTimeout(handleIframeLoad, 100);
    }
  }, [previewHtml, handleIframeLoad]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }
    };
  }, []);

  // Render loading state
  if (loading && !previewHtml) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Generating Preview</h3>
          <p className="text-sm text-gray-500">
            {retryCount > 0 ? `Retry ${retryCount}/${MAX_RETRIES}...` : 'Please wait while we prepare your template...'}
          </p>
          <div className="mt-4 bg-gray-200 rounded-full h-1 w-48 mx-auto overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !previewHtml) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <div className="p-8 text-center">
          <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-red-900 mb-2">Preview Error</h3>
          <p className="text-sm text-red-700 mb-4">{error}</p>
          <div className="space-x-3">
            <button
              onClick={() => fetchPreview()}
              className="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retry
            </button>
            {retryCount < MAX_RETRIES && (
              <span className="text-xs text-red-600">
                {MAX_RETRIES - retryCount} attempts remaining
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render preview
  return (
    <div 
      ref={fullscreenRef}
      className={`relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className} ${
        isFullscreen ? 'fixed inset-0 z-50 bg-black' : ''
      }`}
    >
      {/* Control Bar */}
      {showControls && (
        <div className={`flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200 ${
          isFullscreen ? 'bg-gray-900 border-gray-700' : ''
        }`}>
          {/* Zoom Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleZoomOut}
              disabled={zoom <= MIN_ZOOM}
              className={`p-1 rounded ${
                zoom <= MIN_ZOOM 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : isFullscreen 
                    ? 'text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:bg-gray-200'
              }`}
              title="Zoom Out"
              aria-label="Zoom Out"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
            
            <span className={`text-sm font-medium min-w-[3rem] text-center ${
              isFullscreen ? 'text-white' : 'text-gray-700'
            }`}>
              {zoom}%
            </span>
            
            <button
              onClick={handleZoomIn}
              disabled={zoom >= MAX_ZOOM}
              className={`p-1 rounded ${
                zoom >= MAX_ZOOM 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : isFullscreen 
                    ? 'text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:bg-gray-200'
              }`}
              title="Zoom In"
              aria-label="Zoom In"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
              </svg>
            </button>

            <div className={`w-px h-4 ${isFullscreen ? 'bg-gray-600' : 'bg-gray-300'}`}></div>

            <button
              onClick={handleZoomReset}
              className={`px-2 py-1 text-xs font-medium rounded ${
                isFullscreen 
                  ? 'text-white hover:bg-gray-800' 
                  : 'text-gray-600 hover:bg-gray-200'
              }`}
              title="Reset Zoom (100%)"
            >
              Reset
            </button>

            <button
              onClick={handleZoomFit}
              className={`px-2 py-1 text-xs font-medium rounded ${
                isFullscreen 
                  ? 'text-white hover:bg-gray-800' 
                  : 'text-gray-600 hover:bg-gray-200'
              }`}
              title="Fit to Width"
            >
              Fit
            </button>
          </div>

          {/* Status and Actions */}
          <div className="flex items-center space-x-2">
            {loading && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                <span className={`text-xs ${isFullscreen ? 'text-white' : 'text-gray-500'}`}>
                  Updating...
                </span>
              </div>
            )}

            {error && previewHtml && (
              <button
                onClick={() => fetchPreview()}
                className={`text-xs px-2 py-1 rounded ${
                  isFullscreen 
                    ? 'text-yellow-400 hover:bg-gray-800' 
                    : 'text-yellow-600 hover:bg-yellow-50'
                }`}
                title="Refresh preview"
              >
                ⚠️ Refresh
              </button>
            )}

            <button
              onClick={toggleFullscreen}
              className={`p-1 rounded ${
                isFullscreen 
                  ? 'text-white hover:bg-gray-800' 
                  : 'text-gray-600 hover:bg-gray-200'
              }`}
              title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Enter Fullscreen'}
              aria-label={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
            >
              {isFullscreen ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Preview Container */}
      <div 
        ref={containerRef}
        className={`relative overflow-auto ${
          isFullscreen ? 'h-full bg-gray-100' : 'h-96'
        }`}
        style={{ 
          height: isFullscreen ? 'calc(100vh - 60px)' : undefined 
        }}
      >
        {previewHtml ? (
          <iframe
            ref={iframeRef}
            className="w-full h-full border-none bg-white"
            title={`Preview of ${templateId} template`}
            sandbox="allow-same-origin allow-scripts"
            onLoad={handleIframeLoad}
            style={{
              minHeight: isFullscreen ? '100%' : '600px'
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full bg-gray-50">
            <div className="text-center">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-gray-500">Select a template to see preview</p>
            </div>
          </div>
        )}
      </div>

      {/* Fullscreen Help Overlay */}
      {isFullscreen && (
        <div className="absolute top-20 right-4 bg-gray-900/90 text-white p-3 rounded-lg text-xs space-y-1 pointer-events-none">
          <div><kbd className="bg-gray-700 px-1 rounded">Esc</kbd> Exit fullscreen</div>
          <div><kbd className="bg-gray-700 px-1 rounded">+</kbd> Zoom in</div>
          <div><kbd className="bg-gray-700 px-1 rounded">-</kbd> Zoom out</div>
          <div><kbd className="bg-gray-700 px-1 rounded">0</kbd> Reset zoom</div>
          <div><kbd className="bg-gray-700 px-1 rounded">F</kbd> Fit to width</div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && previewHtml && (
        <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Updating preview...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplatePreview;







