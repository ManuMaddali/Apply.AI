import React, { useState } from 'react'

const OptionalSections = ({ options, onOptionsChange }) => {
  const [showEducationForm, setShowEducationForm] = useState(options.includeEducation)

  const handleEducationToggle = (checked) => {
    setShowEducationForm(checked)
    if (!checked) {
      // Clear education data when unchecked
      onOptionsChange({
        ...options,
        includeEducation: false,
        educationDetails: {
          degree: '',
          institution: '',
          year: '',
          gpa: ''
        }
      })
    } else {
      onOptionsChange({
        ...options,
        includeEducation: true
      })
    }
  }

  const handleEducationChange = (field, value) => {
    onOptionsChange({
      ...options,
      educationDetails: {
        ...options.educationDetails,
        [field]: value
      }
    })
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 transition-all hover:shadow-md">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-orange-50 rounded-xl">
          <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Optional Sections</h2>
      </div>
      
      <div className="space-y-6">
        {/* Professional Summary */}
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={options.includeSummary}
            onChange={(e) => onOptionsChange({
              ...options,
              includeSummary: e.target.checked
            })}
            className="mt-1 h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
          />
          <div className="flex-1">
            <div className="font-medium text-gray-900">Add Professional Summary</div>
            <div className="text-sm text-gray-500 mt-1">
              Generate a compelling summary tailored to each job
            </div>
          </div>
        </label>

        {/* Skills Section */}
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={options.includeSkills}
            onChange={(e) => onOptionsChange({
              ...options,
              includeSkills: e.target.checked
            })}
            className="mt-1 h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
          />
          <div className="flex-1">
            <div className="font-medium text-gray-900">Add Skills Section</div>
            <div className="text-sm text-gray-500 mt-1">
              Include relevant skills based on job requirements
            </div>
          </div>
        </label>

        {/* Education Section */}
        <div>
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={options.includeEducation}
              onChange={(e) => handleEducationToggle(e.target.checked)}
              className="mt-1 h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
            />
            <div className="flex-1">
              <div className="font-medium text-gray-900">Add Education Section</div>
              <div className="text-sm text-gray-500 mt-1">
                Include educational background and achievements
              </div>
            </div>
          </label>

          {/* Education Form */}
          {showEducationForm && (
            <div className="mt-4 ml-7 space-y-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Degree
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.degree}
                    onChange={(e) => handleEducationChange('degree', e.target.value)}
                    placeholder="e.g., Bachelor of Science"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Institution
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.institution}
                    onChange={(e) => handleEducationChange('institution', e.target.value)}
                    placeholder="e.g., Georgia Tech"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Graduation Year
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.year}
                    onChange={(e) => handleEducationChange('year', e.target.value)}
                    placeholder="e.g., 2020"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    GPA <span className="text-gray-400">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.gpa}
                    onChange={(e) => handleEducationChange('gpa', e.target.value)}
                    placeholder="e.g., 3.8/4.0"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OptionalSections 