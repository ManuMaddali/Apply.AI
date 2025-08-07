import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Target,
  Award,
  Clock,
  Users,
  Download,
  Filter,
  RefreshCw,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Star
} from 'lucide-react';

const AnalyticsDashboard = ({ user, onClose }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, [timePeriod]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/analytics/dashboard?time_period=${timePeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const result = await response.json();
      setDashboardData(result.data);
    } catch (err) {
      setError(err.message);
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format = 'json') => {
    try {
      const response = await fetch(`/api/analytics/export?format=${format}&time_period=${timePeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to export data');
      }

      const result = await response.json();
      
      // Create download link
      const dataStr = JSON.stringify(result.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `applyai-analytics-${timePeriod}.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export data');
    }
  };

  const MetricCard = ({ metric, onClick }) => {
    const getTrendIcon = (trend) => {
      switch (trend) {
        case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />;
        case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />;
        default: return <div className="w-4 h-4" />;
      }
    };

    const getTrendColor = (trend) => {
      switch (trend) {
        case 'up': return 'text-green-600';
        case 'down': return 'text-red-600';
        default: return 'text-gray-600';
      }
    };

    return (
      <motion.div
        className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => onClick(metric)}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-700">{metric.name}</h3>
          {getTrendIcon(metric.trend)}
        </div>
        
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-gray-900">
            {typeof metric.value === 'number' ? metric.value.toFixed(1) : metric.value}
            {metric.name.includes('Rate') || metric.name.includes('Score') ? '%' : ''}
          </span>
          <span className={`text-sm font-medium ${getTrendColor(metric.trend)}`}>
            {metric.change > 0 ? '+' : ''}{metric.change.toFixed(1)}%
          </span>
        </div>
        
        <p className="text-xs text-gray-500 mt-2">{metric.description}</p>
      </motion.div>
    );
  };

  const InsightCard = ({ insight }) => {
    const getImpactColor = (score) => {
      if (score >= 80) return 'bg-green-100 text-green-800';
      if (score >= 60) return 'bg-yellow-100 text-yellow-800';
      return 'bg-red-100 text-red-800';
    };

    return (
      <motion.div
        className="bg-white rounded-lg border border-gray-200 p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-gray-900">{insight.category}</span>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact_score)}`}>
            {insight.impact_score.toFixed(0)}% impact
          </span>
        </div>
        
        <p className="text-gray-700 mb-3">{insight.insight}</p>
        
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-sm text-blue-800 font-medium">Recommendation:</p>
          <p className="text-sm text-blue-700 mt-1">{insight.recommendation}</p>
        </div>
      </motion.div>
    );
  };

  const RecommendationCard = ({ recommendation }) => {
    const getPriorityColor = (priority) => {
      switch (priority) {
        case 'high': return 'bg-red-100 text-red-800 border-red-200';
        case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        case 'low': return 'bg-green-100 text-green-800 border-green-200';
        default: return 'bg-gray-100 text-gray-800 border-gray-200';
      }
    };

    const getEffortIcon = (effort) => {
      switch (effort) {
        case 'low': return <CheckCircle className="w-4 h-4 text-green-500" />;
        case 'medium': return <Clock className="w-4 h-4 text-yellow-500" />;
        case 'high': return <AlertCircle className="w-4 h-4 text-red-500" />;
        default: return <Clock className="w-4 h-4 text-gray-500" />;
      }
    };

    return (
      <motion.div
        className="bg-white rounded-lg border border-gray-200 p-6"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="flex items-start justify-between mb-3">
          <h4 className="text-lg font-semibold text-gray-900">{recommendation.title}</h4>
          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(recommendation.priority)}`}>
            {recommendation.priority} priority
          </span>
        </div>
        
        <p className="text-gray-600 mb-4">{recommendation.description}</p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              {getEffortIcon(recommendation.effort)}
              <span className="text-sm text-gray-600">{recommendation.effort} effort</span>
            </div>
            <div className="text-sm text-blue-600 font-medium">
              {recommendation.expected_impact}
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400" />
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-sm w-full mx-4">
          <div className="flex items-center justify-center mb-4">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
          <p className="text-center text-gray-600">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-sm w-full mx-4">
          <div className="flex items-center justify-center mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <p className="text-center text-red-600 mb-4">{error}</p>
          <div className="flex space-x-3">
            <button
              onClick={fetchDashboardData}
              className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Retry
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        className="bg-gray-50 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
      >
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Performance Analytics</h2>
              <p className="text-gray-600 mt-1">
                Insights for {dashboardData?.overview?.date_range?.start} to {dashboardData?.overview?.date_range?.end}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Time Period Selector */}
              <select
                value={timePeriod}
                onChange={(e) => setTimePeriod(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
              
              {/* Export Button */}
              <button
                onClick={() => exportData('json')}
                className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              
              {/* Close Button */}
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-100px)]">
          <div className="p-6 space-y-8">
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Resumes</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData?.overview?.total_resumes_generated}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <Target className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData?.overview?.success_rate}%</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3">
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <Award className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Avg ATS Score</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData?.overview?.avg_ats_score}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3">
                  <div className="bg-yellow-100 p-3 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Improvement</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData?.overview?.improvement_trend}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardData?.key_metrics?.map((metric, index) => (
                  <MetricCard
                    key={index}
                    metric={metric}
                    onClick={setSelectedMetric}
                  />
                ))}
              </div>
            </div>

            {/* Success Insights */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Success Insights</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {dashboardData?.success_insights?.map((insight, index) => (
                  <InsightCard key={index} insight={insight} />
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personalized Recommendations</h3>
              <div className="space-y-4">
                {dashboardData?.recommendations?.map((recommendation, index) => (
                  <RecommendationCard key={index} recommendation={recommendation} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AnalyticsDashboard;
