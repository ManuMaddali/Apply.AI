import React from 'react';

const TemplateSelector = ({ selectedTemplate, onTemplateChange, isPro = false }) => {
  const templates = [
    {
      id: 'modern',
      name: 'Modern',
      description: 'Clean professional design with blue accents',
      color: '#4472C4',
      free: true
    },
    {
      id: 'classic',
      name: 'Classic',
      description: 'Traditional black and white format',
      color: '#000000',
      free: true
    },
    {
      id: 'technical',
      name: 'Technical',
      description: 'Clean layout optimized for tech roles',
      color: '#2d5016',
      free: true
    },
    {
      id: 'executive',
      name: 'Executive',
      description: 'Conservative design for senior roles',
      color: '#1f4e79',
      free: false
    },
    {
      id: 'creative',
      name: 'Creative',
      description: 'Modern design with creative flair',
      color: '#663399',
      free: false
    }
  ];

  const availableTemplates = isPro ? templates : templates.filter(t => t.free);

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Resume Template
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {availableTemplates.map((template) => (
          <div
            key={template.id}
            className={`relative cursor-pointer rounded-lg border p-4 hover:bg-gray-50 ${
              selectedTemplate === template.id
                ? 'border-blue-500 ring-2 ring-blue-500'
                : 'border-gray-300'
            }`}
            onClick={() => onTemplateChange(template.id)}
          >
            <div className="flex items-center space-x-3">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: template.color }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900">
                    {template.name}
                  </p>
                  {!template.free && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Pro
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {template.description}
                </p>
              </div>
            </div>
            {selectedTemplate === template.id && (
              <div className="absolute top-2 right-2">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>
      {!isPro && (
        <p className="text-xs text-gray-500">
          Upgrade to Pro to access Executive and Creative templates
        </p>
      )}
    </div>
  );
};

export default TemplateSelector;
