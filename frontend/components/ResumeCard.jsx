import { useState } from 'react';

export default function ResumeCard({ title, content, cardClass = "bg-white border-gray-200", showDiffHighlights = false, diffData = null }) {
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

  const formatContentWithHighlights = (text) => {
    if (!showDiffHighlights || !diffData) {
      return text;
    }

    // This would implement diff highlighting - simplified version
    const lines = text.split('\n');
    return lines.map((line, index) => {
      // Check if this line has changes (simplified logic)
      const hasChanges = diffData?.detailed_diff?.some(diff => 
        diff.content.toLowerCase().includes(line.toLowerCase().substring(0, 50))
      );
      
      return (
        <div key={index} className={hasChanges ? 'bg-yellow-100 rounded px-1' : ''}>
          {line}
        </div>
      );
    });
  };

  const truncatedContent = content?.length > 500 ? content.substring(0, 500) + '...' : content;
  const displayContent = isExpanded ? content : truncatedContent;

  return (
    <div className={`border rounded-lg shadow-lg p-6 transition-all duration-200 hover:shadow-xl ${cardClass}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {title}
        </h3>
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

      {/* Content */}
      <div className="relative">
        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed max-h-96 overflow-y-auto bg-gray-50 p-4 rounded border">
          {showDiffHighlights && diffData ? formatContentWithHighlights(displayContent) : displayContent}
        </pre>
        
        {!isExpanded && content?.length > 500 && (
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 to-transparent"></div>
        )}
      </div>

      {/* Metadata */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 space-y-1">
          <div>
            <span className="font-medium">Length:</span> {content?.length || 0} characters
          </div>
          <div>
            <span className="font-medium">Words:</span> {content?.split(' ').length || 0}
          </div>
          {diffData && (
            <div>
              <span className="font-medium">Enhancement Score:</span> 
              <span className="ml-1 font-bold text-green-600">
                {diffData.enhancement_score?.overall_score || 'N/A'}/100
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 