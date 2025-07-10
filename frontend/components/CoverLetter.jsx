import React, { useState } from 'react'

const CoverLetter = ({ options, onOptionsChange }) => {
  const [showPersonalizationForm, setShowPersonalizationForm] = useState(options.includeCoverLetter)

  const handleCoverLetterToggle = (checked) => {
    setShowPersonalizationForm(checked)
    if (!checked) {
      // Clear cover letter data when unchecked
      onOptionsChange({
        ...options,
        includeCoverLetter: false,
        coverLetterDetails: {
          tone: 'professional',
          emphasize: 'experience',
          additionalInfo: ''
        }
      })
    } else {
      onOptionsChange({
        ...options,
        includeCoverLetter: true
      })
    }
  }

  const handleCoverLetterChange = (field, value) => {
    onOptionsChange({
      ...options,
      coverLetterDetails: {
        ...options.coverLetterDetails,
        [field]: value
      }
    })
  }

  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90 scroll-optimized">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-lg">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Cover Letter</h2>
          <p className="text-sm text-gray-600 mt-1">Generate personalized cover letters for each application</p>
        </div>
      </div>
      
      <div className="space-y-6">
        {/* Cover Letter Toggle */}
        <label className="flex items-start gap-4 cursor-pointer p-4 rounded-xl bg-gradient-to-r from-indigo-50/50 to-purple-50/50 border border-indigo-200/50 hover:border-indigo-300/50 transition-all duration-200">
          <div className="flex-shrink-0 mt-0.5">
            <input
              type="checkbox"
              checked={options.includeCoverLetter}
              onChange={(e) => handleCoverLetterToggle(e.target.checked)}
              className="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Include Cover Letter
            </div>
            <div className="text-sm text-gray-600 mt-1">
              AI-generated cover letters tailored to each job posting
            </div>
          </div>
        </label>

        {/* Cover Letter Customization Form */}
        {showPersonalizationForm && (
          <div className="space-y-6 p-6 bg-white/70 backdrop-light rounded-xl border border-white/50 animate-fadeIn scroll-optimized">
            <div className="flex items-center gap-3 mb-4">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
              <h3 className="text-lg font-semibold text-gray-900">Personalization Options</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Writing Tone
                </label>
                <div className="space-y-2">
                  {[
                    { value: 'professional', label: 'Professional', desc: 'Formal and business-oriented' },
                    { value: 'enthusiastic', label: 'Enthusiastic', desc: 'Energetic and passionate' },
                    { value: 'confident', label: 'Confident', desc: 'Assertive and self-assured' },
                    { value: 'friendly', label: 'Friendly', desc: 'Warm and approachable' }
                  ].map((tone) => (
                    <label key={tone.value} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="radio"
                        name="tone"
                        value={tone.value}
                        checked={options.coverLetterDetails?.tone === tone.value}
                        onChange={(e) => handleCoverLetterChange('tone', e.target.value)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900">{tone.label}</div>
                        <div className="text-xs text-gray-500">{tone.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Emphasize
                </label>
                <div className="space-y-2">
                  {[
                    { value: 'experience', label: 'Work Experience', desc: 'Highlight professional background' },
                    { value: 'skills', label: 'Technical Skills', desc: 'Focus on abilities and competencies' },
                    { value: 'achievements', label: 'Achievements', desc: 'Showcase accomplishments' },
                    { value: 'education', label: 'Education', desc: 'Emphasize academic background' },
                    { value: 'balanced', label: 'Balanced Approach', desc: 'Mix of experience, skills, and achievements' }
                  ].map((emphasis) => (
                    <label key={emphasis.value} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="radio"
                        name="emphasize"
                        value={emphasis.value}
                        checked={options.coverLetterDetails?.emphasize === emphasis.value}
                        onChange={(e) => handleCoverLetterChange('emphasize', e.target.value)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900">{emphasis.label}</div>
                        <div className="text-xs text-gray-500">{emphasis.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Additional Information <span className="text-gray-400">(optional)</span>
              </label>
              <textarea
                value={options.coverLetterDetails?.additionalInfo || ''}
                onChange={(e) => handleCoverLetterChange('additionalInfo', e.target.value)}
                placeholder="Share any specific details you'd like highlighted in your cover letters...

For example, mention your passion for the company's mission, a relevant project you've worked on, or specific goals that align with the role. This helps create more personalized and compelling cover letters."
                rows={4}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm resize-none bg-white/80 backdrop-light"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CoverLetter 