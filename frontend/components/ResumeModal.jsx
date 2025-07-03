import React from 'react'

const ResumeModal = ({ isOpen, onClose, resume, jobTitle, originalResume }) => {
  if (!isOpen) return null

  const wasEnhanced = (original, tailored) => {
    if (!original || !tailored) return false
    const cleanOriginal = original.replace(/\s+/g, ' ').trim()
    const cleanTailored = tailored.replace(/\s+/g, ' ').trim()
    return cleanOriginal !== cleanTailored
  }

  const highlightNewContent = (original, tailored) => {
    if (!original || !tailored) return tailored

    const normalizeText = (text) => {
      return text
        .toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
    }

    // More sophisticated similarity check
    const calculateSimilarity = (line1, line2) => {
      const words1 = new Set(normalizeText(line1).split(/\s+/).filter(w => w.length > 2))
      const words2 = new Set(normalizeText(line2).split(/\s+/).filter(w => w.length > 2))
      
      if (words1.size === 0 && words2.size === 0) return 1
      if (words1.size === 0 || words2.size === 0) return 0
      
      const intersection = new Set([...words1].filter(x => words2.has(x)))
      return intersection.size / Math.max(words1.size, words2.size)
    }

    // Check if line is significantly different from original
    const isSignificantlyDifferent = (tailoredLine, originalLines) => {
      const trimmedLine = tailoredLine.trim()
      
      // Skip empty lines and headers
      if (!trimmedLine || trimmedLine.length < 10) return false
      
      // Check against all original lines
      let maxSimilarity = 0
      for (const origLine of originalLines) {
        if (origLine.trim().length < 10) continue
        const similarity = calculateSimilarity(tailoredLine, origLine)
        maxSimilarity = Math.max(maxSimilarity, similarity)
      }
      
      // Highlight if similarity is less than 60% (meaning it's been significantly changed)
      return maxSimilarity < 0.6
    }

    // Check if this is likely enhanced/new content
    const isEnhancedContent = (line, lineIndex, allLines) => {
      const trimmedLine = line.trim()
      
      // Skip empty lines
      if (!trimmedLine) return false
      
      // Skip section headers (all caps, short lines)
      if (trimmedLine.length < 50 && trimmedLine === trimmedLine.toUpperCase()) return false
      
      // Skip contact info (contains @ or phone patterns)
      if (trimmedLine.includes('@') || /\(\d{3}\)|\d{3}-\d{3}-\d{4}/.test(trimmedLine)) return false
      
      // Highlight professional summary content (first substantial content)
      if (lineIndex < 20 && trimmedLine.length > 30 && 
          !trimmedLine.includes('•') && !trimmedLine.includes('-') &&
          !trimmedLine.includes(':') && !/^\s*[A-Z\s]+$/.test(trimmedLine)) {
        return true
      }
      
      // Highlight bullet points and substantial content
      if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-') || 
          trimmedLine.startsWith('*') || trimmedLine.length > 40) {
        return true
      }
      
      return false
    }

    const originalLines = original.split('\n').map(line => line.trim()).filter(Boolean)
    const tailoredLines = tailored.split('\n')
    
    let result = ''
    
    tailoredLines.forEach((line, index) => {
      if (!line.trim()) {
        result += '\n'
        return
      }
      
      let shouldHighlight = false
      
      // Check if this line should be considered for highlighting
      if (isEnhancedContent(line, index, tailoredLines)) {
        // Check if it's significantly different from original
        if (isSignificantlyDifferent(line, originalLines)) {
          shouldHighlight = true
        }
      }
      
      if (shouldHighlight) {
        result += `<span class="bg-green-100 px-1 rounded border border-green-300">${line}</span>\n`
      } else {
        result += line + '\n'
      }
    })
    
    return result.trimEnd()
  }

  const isEnhanced = wasEnhanced(originalResume, resume)
  const highlightedResume = isEnhanced ? highlightNewContent(originalResume, resume) : resume

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-gray-50">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">{jobTitle}</h2>
            <div className="text-sm text-gray-600 mt-1">
              {isEnhanced ? (
                <span className="text-green-600 font-medium flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  AI-enhanced resume
                </span>
              ) : (
                <span>Resume preview</span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-light p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            ×
          </button>
        </div>

        {/* Content */}
        {originalResume ? (
          <div className="flex-1 flex overflow-hidden">
            
            {/* Original Resume */}
            <div className="w-1/2 border-r border-gray-100 flex flex-col">
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
                <h3 className="font-medium text-gray-900">Original Resume</h3>
                <p className="text-xs text-gray-500 mt-1">Your uploaded version</p>
              </div>
              <div className="flex-1 overflow-y-auto p-6 bg-white">
                <pre className="text-sm text-gray-700 font-mono leading-relaxed whitespace-pre-wrap break-words">
{originalResume}
                </pre>
              </div>
            </div>

            {/* Tailored Resume */}
            <div className="w-1/2 flex flex-col">
              <div className="bg-blue-50 px-6 py-4 border-b border-gray-100">
                <h3 className="font-medium text-gray-900">Tailored Resume</h3>
                <p className="text-xs text-gray-500 mt-1">Optimized for this position</p>
              </div>
              <div className="flex-1 overflow-y-auto p-6 bg-white">
                <div 
                  className="text-sm text-gray-700 font-mono leading-relaxed whitespace-pre-wrap break-words"
                  dangerouslySetInnerHTML={{ __html: highlightedResume }}
                />
              </div>
            </div>
          </div>
        ) : (
          // Single view
          <div className="flex-1 overflow-y-auto p-8">
            <pre className="text-sm text-gray-700 font-mono leading-relaxed bg-gray-50 p-6 rounded-xl whitespace-pre-wrap break-words">
{resume}
            </pre>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center p-6 border-t border-gray-100 bg-gray-50">
          <div className="text-sm text-gray-600">
            {isEnhanced && (
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-green-100 border border-green-300 mr-2 rounded"></div>
                  New content highlighted
                </span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Close Preview
          </button>
        </div>
      </div>
    </div>
  )
}

export default ResumeModal 