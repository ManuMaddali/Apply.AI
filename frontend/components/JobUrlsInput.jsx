import React from 'react'

const JobUrlsInput = ({ jobUrls, onJobUrlsChange }) => {
  const urlCount = jobUrls.trim().split('\n').filter(line => line.trim()).length

  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90 scroll-optimized">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Job Opportunities</h2>
            <p className="text-sm text-gray-600 mt-1">Add URLs for positions you're interested in</p>
          </div>
        </div>
        {urlCount > 0 && (
          <div className="flex items-center gap-2">
            <div className="text-sm font-semibold text-purple-600 bg-gradient-to-r from-purple-100 to-pink-100 px-4 py-2 rounded-full border border-purple-200">
              {urlCount} {urlCount === 1 ? 'position' : 'positions'}
            </div>
          </div>
        )}
      </div>
      
      <div className="relative">
        <textarea
          value={jobUrls}
          onChange={(e) => onJobUrlsChange(e.target.value)}
          placeholder="Enter job posting URLs here, one per line

• Simply paste the full URL of each job posting you'd like to apply to
• Our AI will automatically extract requirements and tailor your resume
• Support for up to 10 positions at once"
          rows={8}
          className="w-full px-6 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm resize-none bg-gradient-to-br from-gray-50/50 to-purple-50/30 backdrop-light transition-all duration-300"
        />
        
        {/* Floating counter */}
        <div className="absolute top-4 right-4 bg-white/90 backdrop-light rounded-lg px-3 py-1 text-xs font-medium text-gray-600 border border-gray-200">
          {urlCount}/10
        </div>
      </div>
      
      <div className="mt-6 bg-gradient-to-r from-purple-50/50 to-pink-50/50 rounded-xl p-4 border border-purple-100/50">
        <div className="flex items-center gap-3 mb-3">
          <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm font-semibold text-gray-900">Supported Platforms</span>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">LinkedIn</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">Company Sites</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white/60 rounded-lg">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span className="text-sm text-gray-700 font-medium">Job Boards</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default JobUrlsInput 