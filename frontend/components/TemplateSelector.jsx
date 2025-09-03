import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiRequest } from '../utils/api';

const TemplateSelector = ({ selectedTemplate, onTemplateChange, isPro = false }) => {
  // State management
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hoveredTemplate, setHoveredTemplate] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  // Refs for keyboard navigation
  const containerRef = useRef(null);
  const templateRefs = useRef({});
  const previewTimeoutRef = useRef(null);

  // Fetch template metadata from API
  const fetchTemplateMetadata = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest('/api/templates/metadata?include_previews=true');
      
      if (response && response.templates) {
        // Transform API response to component format
        const transformedTemplates = response.templates.map(template => ({
          id: template.id,
          name: template.name,
          description: template.description,
          category: template.category,
          tags: template.tags || [],
          features: template.features || [],
          color_scheme: template.color_scheme,
          layout_type: template.layout_type,
          industry_focus: template.industry_focus || [],
          difficulty_level: template.difficulty_level,
          supports: template.supports || ['html', 'pdf'],
          preview_url: template.preview_urls?.html,
          screenshot_url: template.preview_urls?.png,
          free: template.id === 'modern' || template.id === 'classic', // Only modern and classic are free
          // Color mapping based on template type
          color: getTemplateColor(template.color_scheme, template.id)
        }));
        
        setTemplates(transformedTemplates);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Failed to fetch template metadata:', err);
      setError(err.message);
      
      // Fallback to static templates
      setTemplates([
        {
          id: 'modern',
          name: 'Modern',
          description: 'Clean professional design with blue accents',
          category: 'modern',
          tags: ['modern', 'clean', 'professional'],
          features: ['Modern typography', 'Responsive design'],
          color: '#4472C4',
          free: true
        },
        {
          id: 'classic',
          name: 'Classic',
          description: 'Traditional black and white format',
          category: 'professional',
          tags: ['traditional', 'conservative', 'formal'],
          features: ['ATS-friendly', 'Print-optimized'],
          color: '#000000',
          free: true
        },
        {
          id: 'technical',
          name: 'Technical',
          description: 'Clean layout optimized for tech roles',
          category: 'technical',
          tags: ['technical', 'engineering', 'skills-focused'],
          features: ['Skills highlighting', 'Project showcase'],
          color: '#2d5016',
          free: true
        },
        {
          id: 'executive',
          name: 'Executive',
          description: 'Conservative design for senior roles',
          category: 'executive',
          tags: ['executive', 'sophisticated', 'leadership'],
          features: ['Premium typography', 'Executive styling'],
          color: '#1f4e79',
          free: false
        },
        {
          id: 'creative',
          name: 'Creative',
          description: 'Modern design with creative flair',
          category: 'creative',
          tags: ['creative', 'colorful', 'vibrant'],
          features: ['Colorful gradients', 'Visual elements'],
          color: '#663399',
          free: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Get color based on color scheme
  const getTemplateColor = (colorScheme, templateId) => {
    const colorMap = {
      'monochrome': '#000000',
      'blue-gradient': '#4472C4',
      'multi-color': '#663399',
      'navy-blue': '#1f4e79',
      'tech-blue': '#2d5016'
    };
    
    return colorMap[colorScheme] || colorMap[templateId] || '#4472C4';
  };

  // Load preview image on hover
  const loadPreviewImage = useCallback(async (template) => {
    if (!template.screenshot_url || previewLoading) return;
    
    try {
      setPreviewLoading(true);
      
      // Create a promise-based image loader
      const loadImage = () => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(img.src);
          img.onerror = reject;
          img.src = template.screenshot_url;
        });
      };
      
      const imageSrc = await loadImage();
      setPreviewImage(imageSrc);
    } catch (err) {
      console.error('Failed to load preview image:', err);
      setPreviewImage(null);
    } finally {
      setPreviewLoading(false);
    }
  }, [previewLoading]);

  // Handle mouse enter with debounced preview loading
  const handleMouseEnter = useCallback((template) => {
    setHoveredTemplate(template);
    
    // Clear any existing timeout
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current);
    }
    
    // Load preview after a short delay to avoid loading on quick hovers
    previewTimeoutRef.current = setTimeout(() => {
      loadPreviewImage(template);
    }, 300);
  }, [loadPreviewImage]);

  // Handle mouse leave
  const handleMouseLeave = useCallback(() => {
    setHoveredTemplate(null);
    setPreviewImage(null);
    
    // Clear timeout if user leaves before preview loads
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current);
    }
  }, []);

  // Keyboard navigation
  const handleKeyDown = useCallback((event) => {
    const availableTemplates = isPro ? templates : templates.filter(t => t.free);
    
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev < availableTemplates.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev > 0 ? prev - 1 : availableTemplates.length - 1
        );
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0 && availableTemplates[focusedIndex]) {
          onTemplateChange(availableTemplates[focusedIndex].id);
        }
        break;
      case 'Escape':
        setFocusedIndex(-1);
        break;
    }
  }, [templates, isPro, focusedIndex, onTemplateChange]);

  // Focus management
  useEffect(() => {
    const availableTemplates = isPro ? templates : templates.filter(t => t.free);
    if (focusedIndex >= 0 && availableTemplates[focusedIndex]) {
      const templateId = availableTemplates[focusedIndex].id;
      templateRefs.current[templateId]?.focus();
    }
  }, [focusedIndex, templates, isPro]);

  // Load templates on mount
  useEffect(() => {
    fetchTemplateMetadata();
  }, [fetchTemplateMetadata]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (previewTimeoutRef.current) {
        clearTimeout(previewTimeoutRef.current);
      }
    };
  }, []);

  const availableTemplates = isPro ? templates : templates.filter(t => t.free);

  if (loading) {
    return (
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Resume Template
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 rounded-lg h-32"></div>
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-500" aria-live="polite">
          Loading templates...
        </p>
      </div>
    );
  }

  if (error && templates.length === 0) {
    return (
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Resume Template
        </label>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-600">
            Failed to load templates. Please try refreshing the page.
          </p>
          <button
            onClick={fetchTemplateMetadata}
            className="mt-2 text-sm text-red-700 hover:text-red-800 underline"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4" ref={containerRef}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Resume Template
        </label>
        {error && (
          <span className="text-xs text-amber-600" title="Using cached templates">
            ⚠️ Limited connectivity
          </span>
        )}
      </div>

      {/* Template Grid */}
      <div 
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        role="radiogroup"
        aria-label="Resume template selection"
        onKeyDown={handleKeyDown}
      >
        {availableTemplates.map((template, index) => (
          <div
            key={template.id}
            ref={el => templateRefs.current[template.id] = el}
            className={`relative cursor-pointer rounded-xl border-2 transition-all duration-200 group ${
              selectedTemplate === template.id
                ? 'border-blue-500 ring-4 ring-blue-500/20 bg-blue-50'
                : hoveredTemplate?.id === template.id
                ? 'border-gray-400 shadow-lg bg-gray-50'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
            } ${focusedIndex === index ? 'ring-2 ring-offset-2 ring-blue-500' : ''}`}
            onClick={() => onTemplateChange(template.id)}
            onMouseEnter={() => handleMouseEnter(template)}
            onMouseLeave={handleMouseLeave}
            tabIndex={0}
            role="radio"
            aria-checked={selectedTemplate === template.id}
            aria-labelledby={`template-${template.id}-name`}
            aria-describedby={`template-${template.id}-description`}
          >
            {/* Template Thumbnail */}
            <div className="aspect-[3/4] bg-gradient-to-br from-gray-50 to-gray-100 rounded-t-xl overflow-hidden relative">
              {template.screenshot_url ? (
                <div className="w-full h-full bg-white flex items-center justify-center">
                  <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div
                    className="w-16 h-20 rounded-sm opacity-80"
                    style={{ backgroundColor: template.color }}
                  />
                </div>
              )}

              {/* Loading overlay for preview */}
              {hoveredTemplate?.id === template.id && previewLoading && (
                <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                </div>
              )}

              {/* Pro badge */}
              {!template.free && (
                <div className="absolute top-2 right-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 shadow-sm">
                    Pro
                  </span>
                </div>
              )}

              {/* Selected indicator */}
              {selectedTemplate === template.id && (
                <div className="absolute top-2 left-2">
                  <div className="bg-blue-500 rounded-full p-1">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </div>

            {/* Template Information */}
            <div className="p-4 space-y-3">
              {/* Name and Category */}
              <div>
                <h3 
                  id={`template-${template.id}-name`}
                  className="font-semibold text-gray-900 text-sm"
                >
                  {template.name}
                </h3>
                <p 
                  id={`template-${template.id}-description`}
                  className="text-xs text-gray-600 mt-1"
                >
                  {template.description}
                </p>
              </div>

              {/* Tags */}
              {template.tags && template.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {template.tags.slice(0, 3).map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {tag}
                    </span>
                  ))}
                  {template.tags.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{template.tags.length - 3} more
                    </span>
                  )}
                </div>
              )}

              {/* Features */}
              {template.features && template.features.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs font-medium text-gray-700">Features:</p>
                  <ul className="text-xs text-gray-600 space-y-0.5">
                    {template.features.slice(0, 2).map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <svg className="w-3 h-3 text-green-500 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Industry Focus */}
              {template.industry_focus && template.industry_focus.length > 0 && (
                <div className="pt-2 border-t border-gray-100">
                  <p className="text-xs text-gray-500">
                    Best for: {template.industry_focus.slice(0, 2).join(', ')}
                  </p>
                </div>
              )}
            </div>

            {/* Hover effect overlay */}
            <div className="absolute inset-0 rounded-xl transition-opacity duration-200 opacity-0 group-hover:opacity-100 pointer-events-none">
              <div className="absolute inset-0 rounded-xl ring-2 ring-blue-300"></div>
            </div>
          </div>
        ))}
      </div>

      {/* Preview Modal */}
      {hoveredTemplate && previewImage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" style={{ pointerEvents: 'none' }}>
          <div className="bg-white rounded-lg shadow-2xl max-w-2xl max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {hoveredTemplate.name} Preview
              </h3>
              <p className="text-sm text-gray-600">{hoveredTemplate.description}</p>
            </div>
            <div className="p-4">
              <img
                src={previewImage}
                alt={`Preview of ${hoveredTemplate.name} template`}
                className="w-full h-auto max-h-96 object-contain"
                onError={() => setPreviewImage(null)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="space-y-2">
        {!isPro && (
          <p className="text-xs text-gray-500">
            <span className="inline-flex items-center">
              <svg className="w-3 h-3 text-yellow-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Upgrade to Pro to access {templates.filter(t => !t.free).length} premium templates
            </span>
          </p>
        )}
        
        <p className="text-xs text-gray-400">
          Use arrow keys to navigate, Enter to select, or hover for preview
        </p>
      </div>

      {/* Screen reader announcements */}
      <div className="sr-only" aria-live="polite">
        {selectedTemplate && (
          <span>
            Selected template: {templates.find(t => t.id === selectedTemplate)?.name}
          </span>
        )}
      </div>
    </div>
  );
};

export default TemplateSelector;
