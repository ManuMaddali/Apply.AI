import React from 'react'

const ResultCard = React.memo(({ result, onView, onDownloadPDF, onDownloadCoverLetter, onDownloadText, includeCoverLetter, tailoringMode }) => {

  const getJobDetails = () => {
    let company = 'Company'
    let jobTitle = result.job_title || 'Position'
    
    if (result.job_url) {
      try {
        const url = new URL(result.job_url)
        const hostname = url.hostname.toLowerCase()
        
        if (hostname.includes('linkedin.com')) {
          company = 'LinkedIn'
        } else if (hostname.includes('lever.co')) {
          company = 'Lever'
        } else if (hostname.includes('greenhouse.io')) {
          company = 'Greenhouse'
        } else if (hostname.includes('workday.com')) {
          company = 'Workday'
        } else if (hostname.includes('bamboohr.com')) {
          company = 'BambooHR'
        } else {
          // Extract main domain name
          const parts = hostname.split('.')
          if (parts.length >= 2) {
            company = parts[parts.length - 2]
            company = company.charAt(0).toUpperCase() + company.slice(1)
          }
        }
      } catch (e) {
        // If URL parsing fails, keep default
      }
    }
    
    // If we have a job title that looks like a company name, use it
    if (result.job_title && result.job_title.length < 50) {
      const titleWords = result.job_title.split(' ')
      if (titleWords.length <= 3) {
        company = result.job_title
        jobTitle = 'Position'
      }
    }
    
    return { company, jobTitle }
  }

  const { company, jobTitle } = getJobDetails()

  if (result.status === 'processing') {
    return (
      <div className="bg-white/70 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 transition-all duration-300 animate-pulse scroll-optimized">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-400 rounded-xl flex items-center justify-center shadow-md">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 112 2v6a2 2 0 11-2 2v-2M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m-8 0V6a2 2 0 00-2 2v6a2 2 0 002 2v-2" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{company}</h3>
              <p className="text-sm text-gray-600 mt-1">{jobTitle}</p>
              {includeCoverLetter && (
                <p className="text-xs text-indigo-600 mt-1">+ Cover letter</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center text-blue-600 bg-blue-50 px-3 py-2 rounded-full">
              <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-sm font-medium">Tailoring...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (result.status === 'failed') {
    return (
      <div className="bg-white/70 backdrop-light rounded-2xl shadow-lg border border-red-200/50 p-6 transition-all duration-300 scroll-optimized">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-red-400 to-red-500 rounded-xl flex items-center justify-center shadow-md">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.232 16.5c-.77.833.19 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{company}</h3>
              <p className="text-sm text-gray-600 mt-1">{jobTitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Failed
            </span>
          </div>
        </div>
        <div className="mt-4 text-sm text-red-600 bg-red-50/80 backdrop-light p-3 rounded-lg border border-red-200">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {result.error || 'Unable to process this job posting'}
          </div>
        </div>
      </div>
    )
  }

  const hasCoverLetter = includeCoverLetter && result.cover_letter && result.cover_letter.trim()

  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-6 transition-all duration-300 hover:shadow-xl hover:bg-white/90 interactive-card scroll-optimized">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-green-500 rounded-xl flex items-center justify-center shadow-md">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">{company}</h3>
            <p className="text-sm text-gray-600 mt-1 truncate">{jobTitle}</p>
            <div className="flex items-center gap-3 mt-1">
              {hasCoverLetter && (
                <div className="flex items-center gap-1">
                  <svg className="w-3 h-3 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                  <span className="text-xs text-indigo-600 font-medium">Cover letter</span>
                </div>
              )}
              {tailoringMode && (
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${
                    tailoringMode === 'heavy' ? 'bg-purple-500' : 'bg-blue-500'
                  }`}></div>
                  <span className={`text-xs font-medium ${
                    tailoringMode === 'heavy' ? 'text-purple-600' : 'text-blue-600'
                  }`}>
                    {tailoringMode === 'heavy' ? 'Heavy tailoring' : 'Light tailoring'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center text-green-600 bg-green-50 px-3 py-2 rounded-full">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium">Ready</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 justify-end flex-wrap">
        {/* Feature Flag: View with Highlights - Disabled for now */}
        {false && (
          <button
            onClick={() => onView(result)}
            className="flex-1 bg-gray-50 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            View with Highlights
          </button>
        )}
        
        <button
          onClick={() => onDownloadPDF(result)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200 text-sm font-medium flex items-center gap-2 shadow-md hover:shadow-lg"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clipRule="evenodd" />
          </svg>
          Resume
        </button>

        {hasCoverLetter && (
          <button
            onClick={() => onDownloadCoverLetter(result)}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 text-sm font-medium flex items-center gap-2 shadow-md hover:shadow-lg"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            Cover
          </button>
        )}
        
        <button
          onClick={() => onDownloadText(result)}
          className="bg-gradient-to-r from-gray-500 to-gray-600 text-white px-4 py-2 rounded-lg hover:from-gray-600 hover:to-gray-700 transition-all duration-200 text-sm font-medium flex items-center gap-2 shadow-md hover:shadow-lg"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          TXT
        </button>
      </div>
    </div>
  )
})

export default ResultCard 