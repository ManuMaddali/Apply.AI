import React from 'react'

const OutputSettings = ({ outputFormat, onFormatChange }) => {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 transition-all hover:shadow-md">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-green-50 rounded-xl">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Output Format</h2>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Choose download format
          </label>
          <select
            value={outputFormat}
            onChange={(e) => onFormatChange(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-gray-900"
          >
            <option value="text">PDF Format</option>
            <option value="files">Multiple Formats (PDF + DOCX)</option>
          </select>
        </div>
        
        <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
          <strong>PDF Format:</strong> Professional PDF files ready for submission<br/>
          <strong>Multiple Formats:</strong> PDF and DOCX files for maximum compatibility
        </div>
      </div>
    </div>
  )
}

export default OutputSettings 