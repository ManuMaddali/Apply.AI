import React, { useState } from 'react'

const ResultCard = ({ result, onView, onDownloadPDF, onDownloadText }) => {
  const [showDropdown, setShowDropdown] = useState(false)

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
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 transition-all">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-medium text-gray-900">{company}</h3>
            <p className="text-sm text-gray-500 mt-1">{jobTitle}</p>
          </div>
          <div className="ml-4">
            <div className="flex items-center text-blue-600">
              <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-sm font-medium">✨ Tailoring resume for {company}...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (result.status === 'failed') {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-red-100 p-6 transition-all">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-medium text-gray-900">{company}</h3>
            <p className="text-sm text-gray-500 mt-1">{jobTitle}</p>
          </div>
          <div className="ml-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Failed
            </span>
          </div>
        </div>
        <div className="mt-3 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
          {result.error || 'An error occurred while processing this job'}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 transition-all hover:shadow-lg">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-900">{company}</h3>
          <p className="text-sm text-gray-500 mt-1">{jobTitle}</p>
        </div>
        <div className="ml-4 flex items-center">
          <span className="text-sm font-medium text-green-600 flex items-center gap-1">
            ✅ Tailored resume ready!
          </span>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-3">
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
        
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-10">
              <button
                onClick={() => {
                  onDownloadPDF(result)
                  setShowDropdown(false)
                }}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clipRule="evenodd" />
                </svg>
                Download as PDF
              </button>
              <button
                onClick={() => {
                  onDownloadText(result)
                  setShowDropdown(false)
                }}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download as Text
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ResultCard 