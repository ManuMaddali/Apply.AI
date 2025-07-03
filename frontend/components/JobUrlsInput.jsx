import React from 'react'

const JobUrlsInput = ({ jobUrls, onJobUrlsChange }) => {
  const urlCount = jobUrls.trim().split('\n').filter(line => line.trim()).length

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 transition-all hover:shadow-md">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-purple-50 rounded-xl">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Job Links</h2>
        </div>
        {urlCount > 0 && (
          <div className="text-sm font-medium text-purple-600 bg-purple-50 px-3 py-1 rounded-lg">
            {urlCount} {urlCount === 1 ? 'job' : 'jobs'}
          </div>
        )}
      </div>
      
      <textarea
        value={jobUrls}
        onChange={(e) => onJobUrlsChange(e.target.value)}
        placeholder="Add job posting links here (one per line)

Examples:
• LinkedIn job posts
• Company career pages  
• Job board listings

Up to 10 positions"
        rows={6}
        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm resize-none"
      />
      
      <div className="mt-3 text-xs text-gray-500">
        Paste job URLs from LinkedIn, company websites, or job boards
      </div>
    </div>
  )
}

export default JobUrlsInput 