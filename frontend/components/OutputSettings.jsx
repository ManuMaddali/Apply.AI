import React from 'react'

const OutputSettings = ({ outputFormat, onFormatChange }) => {
  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90 scroll-optimized">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl shadow-lg">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Output Format</h2>
          <p className="text-sm text-gray-600 mt-1">Choose your preferred download format</p>
        </div>
      </div>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Download Format
          </label>
          <div className="relative">
            <select
              value={outputFormat}
              onChange={(e) => onFormatChange(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-gradient-to-r from-gray-50/50 to-green-50/30 backdrop-light text-gray-900 font-medium appearance-none cursor-pointer transition-all duration-200"
            >
              <option value="text">📄 PDF Format</option>
              <option value="docx">📝 Word Format</option>
              <option value="files">📁 Both (PDF + Word)</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-50/80 to-teal-50/80 backdrop-light p-4 rounded-xl border border-green-200/50">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-2 h-2 bg-gradient-to-r from-green-500 to-teal-500 rounded-full mt-2"></div>
            <div className="text-sm text-gray-700">
              <div className="font-semibold text-gray-900 mb-2">Format Details</div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span><strong>PDF Format:</strong> Professional, ready-to-submit documents</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span><strong>Word Format:</strong> Editable documents for further customization</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span><strong>Both Formats:</strong> PDF + Word for maximum flexibility</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OutputSettings 