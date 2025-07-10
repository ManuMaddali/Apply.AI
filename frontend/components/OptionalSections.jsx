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
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90 scroll-optimized">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl shadow-lg">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Enhance Your Resume</h2>
          <p className="text-sm text-gray-600 mt-1">✨ Smart enhancement - improves existing sections or adds new ones</p>
        </div>
      </div>
      
      <div className="space-y-6">
        {/* Professional Summary */}
        <label className="flex items-start gap-4 cursor-pointer p-4 rounded-xl bg-gradient-to-r from-orange-50/50 to-red-50/50 border border-orange-200/50 hover:border-orange-300/50 transition-all duration-200">
          <div className="flex-shrink-0 mt-0.5">
            <input
              type="checkbox"
              checked={options.includeSummary}
              onChange={(e) => onOptionsChange({
                ...options,
                includeSummary: e.target.checked
              })}
              className="h-5 w-5 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 flex items-center gap-2">
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Professional Summary
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Enhance existing summary or create new one with job-specific keywords
            </div>
          </div>
        </label>

        {/* Skills Section */}
        <label className="flex items-start gap-4 cursor-pointer p-4 rounded-xl bg-gradient-to-r from-blue-50/50 to-purple-50/50 border border-blue-200/50 hover:border-blue-300/50 transition-all duration-200">
          <div className="flex-shrink-0 mt-0.5">
            <input
              type="checkbox"
              checked={options.includeSkills}
              onChange={(e) => onOptionsChange({
                ...options,
                includeSkills: e.target.checked
              })}
              className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Skills Section
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Optimize existing skills section or add new one with job-relevant abilities
            </div>
          </div>
        </label>

        {/* Education Section */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-green-50/50 to-teal-50/50 border border-green-200/50 hover:border-green-300/50 transition-all duration-200">
          <label className="flex items-start gap-4 cursor-pointer">
            <div className="flex-shrink-0 mt-0.5">
              <input
                type="checkbox"
                checked={options.includeEducation}
                onChange={(e) => handleEducationToggle(e.target.checked)}
                className="h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-gray-900 flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                </svg>
                Education Section
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Improve existing education section or add new one with provided details
              </div>
            </div>
          </label>

          {/* Education Form */}
          {showEducationForm && (
            <div className="mt-6 space-y-4 p-6 bg-white/70 backdrop-light rounded-xl border border-white/50 animate-fadeIn scroll-optimized">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Degree
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.degree}
                    onChange={(e) => handleEducationChange('degree', e.target.value)}
                    placeholder="e.g., Bachelor of Science"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-light"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Institution
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.institution}
                    onChange={(e) => handleEducationChange('institution', e.target.value)}
                    placeholder="e.g., Georgia Tech"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-light"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Graduation Year
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.year}
                    onChange={(e) => handleEducationChange('year', e.target.value)}
                    placeholder="e.g., 2020"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-light"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    GPA <span className="text-gray-400">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={options.educationDetails.gpa}
                    onChange={(e) => handleEducationChange('gpa', e.target.value)}
                    placeholder="e.g., 3.8/4.0"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-light"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Helpful Info Note */}
        <div className="mt-4 p-3 bg-blue-50/50 border border-blue-200/50 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-xs text-blue-700">
              <strong>Smart Enhancement:</strong> Check any section to improve it! The AI automatically detects what's already in your resume and enhances existing content or adds missing sections.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OptionalSections 