import React from 'react';

const ATSScoreDisplay = ({ score, grade, components, recommendations }) => {
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 80) return 'bg-blue-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (!score && score !== 0) return null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">ATS Compatibility Score</h3>
        <div className={`px-3 py-1 rounded-full ${getScoreBackground(score)}`}>
          <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
            {score}/100
          </span>
          <span className={`ml-2 text-sm font-medium ${getScoreColor(score)}`}>
            Grade {grade}
          </span>
        </div>
      </div>

      {components && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(components.keyword_match || 0)}
            </div>
            <div className="text-xs text-gray-500">Keyword Match</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(components.formatting || 0)}
            </div>
            <div className="text-xs text-gray-500">Formatting</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(components.structure || 0)}
            </div>
            <div className="text-xs text-gray-500">Structure</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(components.readability || 0)}
            </div>
            <div className="text-xs text-gray-500">Readability</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(components.completeness || 0)}
            </div>
            <div className="text-xs text-gray-500">Completeness</div>
          </div>
        </div>
      )}

      {recommendations && recommendations.length > 0 && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h4>
          <ul className="space-y-1">
            {recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ATSScoreDisplay;
