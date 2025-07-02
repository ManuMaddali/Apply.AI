import { useState } from 'react';

export default function ResumeCard({ 
  title, 
  content, 
  cardClass = "bg-white border-gray-200", 
  showDiffHighlights = false, 
  diffData = null,
  originalContent = null,
  enhancementScore = null,
  isEnhanced = false
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Simple change detection for summary display
  const getChangesSummary = () => {
    if (!originalContent || !content) return null;
    
    const originalLines = originalContent.split('\n').filter(line => line.trim());
    const contentLines = content.split('\n').filter(line => line.trim());
    
    let addedLines = 0;
    let modifiedLines = 0;
    
    // Simple comparison
    contentLines.forEach((line, index) => {
      const originalLine = originalLines[index];
      if (!originalLine) {
        addedLines++;
      } else if (line !== originalLine) {
        modifiedLines++;
      }
    });
    
    return { addedLines, modifiedLines, totalChanges: addedLines + modifiedLines };
  };

  const changes = showDiffHighlights ? getChangesSummary() : null;
  const truncatedContent = content?.length > 500 ? content.substring(0, 500) + '...' : content;
  const displayContent = isExpanded ? content : truncatedContent;

  return (
    <div className={`border rounded-lg shadow-lg p-6 transition-all duration-200 hover:shadow-xl ${cardClass} ${isEnhanced ? 'ring-2 ring-blue-200' : ''}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-900">
            {title}
          </h3>
          {isEnhanced && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
              ✨ AI Enhanced
            </span>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleCopy}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              copySuccess 
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {copySuccess ? '✅ Copied!' : '📋 Copy'}
          </button>
          
          {content?.length > 500 && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
            >
              {isExpanded ? '📄 Show Less' : '📄 Show More'}
            </button>
          )}
        </div>
      </div>

      {/* Changes Summary (if diff highlighting enabled) */}
      {changes && changes.totalChanges > 0 && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="text-sm font-medium text-blue-900 mb-1">
            🎯 AI Improvements Applied:
          </div>
          <div className="flex flex-wrap gap-3 text-xs text-blue-700">
            {changes.addedLines > 0 && (
              <span className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
                {changes.addedLines} new sections
              </span>
            )}
            {changes.modifiedLines > 0 && (
              <span className="flex items-center">
                <div className="w-2 h-2 bg-blue-400 rounded-full mr-1"></div>
                {changes.modifiedLines} enhanced sections
              </span>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="relative">
        <div className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed max-h-96 overflow-y-auto bg-gray-50 p-4 rounded border">
          {displayContent}
        </div>
        
        {!isExpanded && content?.length > 500 && (
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 to-transparent"></div>
        )}
      </div>

      {/* Enhanced Metadata */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500">
          <div>
            <span className="font-medium">Length:</span> {content?.length || 0} chars
          </div>
          <div>
            <span className="font-medium">Words:</span> {content?.split(' ').length || 0}
          </div>
          {enhancementScore && (
            <div>
              <span className="font-medium">Enhancement:</span> 
              <span className="ml-1 font-bold text-green-600">
                {enhancementScore}/100
              </span>
            </div>
          )}
          {changes && changes.totalChanges > 0 && (
            <div>
              <span className="font-medium">Changes:</span> 
              <span className="ml-1 font-medium text-blue-600">
                {changes.totalChanges} sections
              </span>
            </div>
          )}
        </div>
        
        {/* Additional Enhancement Details */}
        {isEnhanced && (
          <div className="mt-3 p-2 bg-blue-50 rounded text-xs">
            <div className="font-medium text-blue-900 mb-1">✨ AI Enhancements Applied:</div>
            <div className="text-blue-700 space-y-1">
              <div>✓ RAG-powered content optimization</div>
              <div>✓ Industry-specific keyword enhancement</div>
              <div>✓ Structure and formatting improvements</div>
              <div>✓ ATS compatibility optimization</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 