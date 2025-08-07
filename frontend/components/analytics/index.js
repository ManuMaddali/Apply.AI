/**
 * Analytics Components Index
 * Exports all analytics and insights system components
 */

export { default as ATSScoringSystem } from './ATSScoringSystem';
export { default as KeywordAnalysisEngine } from './KeywordAnalysisEngine';
export { default as TransformationMetricsDashboard } from './TransformationMetricsDashboard';

// Re-export individual components for granular imports
export { 
  LiveATSScoreUpdates,
  SectionBreakdown,
  ScoreHistory 
} from './ATSScoringSystem';

export {
  KeywordOverview,
  KeywordCategories,
  KeywordList,
  KeywordRecommendations
} from './KeywordAnalysisEngine';

export {
  DashboardHeader,
  OverviewMetrics,
  CategoryBreakdown,
  TimelineAnalysis,
  ComparativeAnalysis,
  InterviewRatePrediction
} from './TransformationMetricsDashboard';