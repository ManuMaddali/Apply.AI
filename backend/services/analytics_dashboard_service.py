"""
Analytics Dashboard Service
Provides comprehensive performance analytics and insights for users
Phase 3: Advanced analytics with success tracking, optimization metrics, and personalized recommendations
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class AnalyticsMetric:
    """Analytics metric data structure"""
    name: str
    value: float
    change: float  # Percentage change from previous period
    trend: str     # 'up', 'down', 'stable'
    description: str

@dataclass
class SuccessInsight:
    """Success insight data structure"""
    category: str
    insight: str
    impact_score: float  # 0-100
    recommendation: str
    data_points: List[Dict[str, Any]]

class AnalyticsDashboardService:
    """Advanced analytics dashboard service for ApplyAI"""
    
    def __init__(self):
        self.metrics_cache = {}
        self.cache_expiry = timedelta(minutes=15)
        
    async def get_dashboard_overview(self, user_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        
        # Calculate time range
        end_date = datetime.now()
        if time_period == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_period == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get all metrics in parallel
        metrics_tasks = [
            self._get_success_metrics(user_id, start_date, end_date),
            self._get_optimization_metrics(user_id, start_date, end_date),
            self._get_usage_metrics(user_id, start_date, end_date),
            self._get_template_performance(user_id, start_date, end_date),
            self._get_ats_score_trends(user_id, start_date, end_date),
            self._get_keyword_optimization_insights(user_id, start_date, end_date)
        ]
        
        results = await asyncio.gather(*metrics_tasks)
        
        success_metrics, optimization_metrics, usage_metrics, template_performance, ats_trends, keyword_insights = results
        
        # Generate insights and recommendations
        insights = await self._generate_success_insights(user_id, results)
        recommendations = await self._generate_personalized_recommendations(user_id, results)
        
        return {
            "overview": {
                "time_period": time_period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_resumes_generated": usage_metrics.get("total_resumes", 0),
                "avg_ats_score": optimization_metrics.get("avg_ats_score", 0),
                "success_rate": success_metrics.get("overall_success_rate", 0),
                "improvement_trend": success_metrics.get("improvement_trend", "stable")
            },
            "key_metrics": [
                AnalyticsMetric(
                    name="Success Rate",
                    value=success_metrics.get("overall_success_rate", 0),
                    change=success_metrics.get("success_rate_change", 0),
                    trend=success_metrics.get("success_trend", "stable"),
                    description="Percentage of applications that led to interviews"
                ).__dict__,
                AnalyticsMetric(
                    name="ATS Score",
                    value=optimization_metrics.get("avg_ats_score", 0),
                    change=optimization_metrics.get("ats_score_change", 0),
                    trend=optimization_metrics.get("ats_trend", "stable"),
                    description="Average ATS compatibility score"
                ).__dict__,
                AnalyticsMetric(
                    name="Keyword Match",
                    value=keyword_insights.get("avg_keyword_match", 0),
                    change=keyword_insights.get("keyword_match_change", 0),
                    trend=keyword_insights.get("keyword_trend", "stable"),
                    description="Average keyword matching with job descriptions"
                ).__dict__,
                AnalyticsMetric(
                    name="Template Effectiveness",
                    value=template_performance.get("best_template_score", 0),
                    change=template_performance.get("template_score_change", 0),
                    trend=template_performance.get("template_trend", "stable"),
                    description="Performance of your most effective template"
                ).__dict__
            ],
            "success_insights": insights,
            "recommendations": recommendations,
            "detailed_metrics": {
                "success_metrics": success_metrics,
                "optimization_metrics": optimization_metrics,
                "usage_metrics": usage_metrics,
                "template_performance": template_performance,
                "ats_trends": ats_trends,
                "keyword_insights": keyword_insights
            }
        }
    
    async def _get_success_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate success rate metrics"""
        # Mock data for now - in production, this would query the database
        mock_data = {
            "total_applications": 45,
            "interviews_received": 12,
            "offers_received": 3,
            "overall_success_rate": 26.7,  # interviews/applications * 100
            "offer_rate": 6.7,  # offers/applications * 100
            "success_rate_change": 8.3,  # Improvement from previous period
            "success_trend": "up",
            "weekly_breakdown": [
                {"week": "Week 1", "applications": 12, "interviews": 3, "success_rate": 25.0},
                {"week": "Week 2", "applications": 11, "interviews": 4, "success_rate": 36.4},
                {"week": "Week 3", "applications": 10, "interviews": 2, "success_rate": 20.0},
                {"week": "Week 4", "applications": 12, "interviews": 3, "success_rate": 25.0}
            ],
            "improvement_trend": "up"
        }
        return mock_data
    
    async def _get_optimization_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate optimization metrics"""
        mock_data = {
            "avg_ats_score": 84.2,
            "ats_score_change": 12.5,
            "ats_trend": "up",
            "score_distribution": {
                "90-100": 15,
                "80-89": 20,
                "70-79": 8,
                "60-69": 2,
                "below_60": 0
            },
            "optimization_impact": {
                "keyword_optimization": 15.2,  # ATS score improvement
                "formatting_improvements": 8.7,
                "structure_enhancements": 6.3
            },
            "best_performing_optimizations": [
                {"optimization": "Technical keywords", "impact": 18.5},
                {"optimization": "Bullet point formatting", "impact": 12.3},
                {"optimization": "Section organization", "impact": 9.7}
            ]
        }
        return mock_data
    
    async def _get_usage_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate usage metrics"""
        mock_data = {
            "total_resumes": 45,
            "total_cover_letters": 32,
            "total_sessions": 28,
            "avg_resumes_per_session": 1.6,
            "most_active_days": ["Tuesday", "Wednesday", "Thursday"],
            "peak_usage_hours": ["10:00-12:00", "14:00-16:00"],
            "feature_usage": {
                "batch_processing": 18,
                "heavy_mode_tailoring": 12,
                "cover_letter_generation": 32,
                "template_switching": 8
            },
            "time_saved_estimate": 15.5  # Hours saved using ApplyAI
        }
        return mock_data
    
    async def _get_template_performance(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze template performance"""
        mock_data = {
            "template_usage": {
                "modern": {"count": 18, "avg_ats_score": 86.2, "success_rate": 28.5},
                "executive": {"count": 12, "avg_ats_score": 88.7, "success_rate": 31.2},
                "technical": {"count": 10, "avg_ats_score": 82.1, "success_rate": 22.8},
                "creative": {"count": 3, "avg_ats_score": 79.3, "success_rate": 18.5},
                "classic": {"count": 2, "avg_ats_score": 81.0, "success_rate": 25.0}
            },
            "best_template": "executive",
            "best_template_score": 88.7,
            "template_score_change": 5.2,
            "template_trend": "up",
            "recommendations": [
                "Executive template shows highest ATS scores and success rates",
                "Consider using Modern template for tech roles",
                "Creative template may need optimization for better ATS compatibility"
            ]
        }
        return mock_data
    
    async def _get_ats_score_trends(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze ATS score trends over time"""
        mock_data = {
            "daily_scores": [
                {"date": "2024-01-01", "avg_score": 78.5, "count": 3},
                {"date": "2024-01-02", "avg_score": 82.1, "count": 2},
                {"date": "2024-01-03", "avg_score": 85.3, "count": 4},
                {"date": "2024-01-04", "avg_score": 87.2, "count": 3},
                {"date": "2024-01-05", "avg_score": 84.8, "count": 2}
            ],
            "component_trends": {
                "keyword_match": {"current": 85.2, "change": 8.7, "trend": "up"},
                "formatting": {"current": 92.1, "change": 2.3, "trend": "up"},
                "structure": {"current": 88.5, "change": 5.1, "trend": "up"},
                "readability": {"current": 86.3, "change": 3.8, "trend": "up"},
                "completeness": {"current": 91.7, "change": 1.2, "trend": "stable"}
            },
            "improvement_areas": [
                {"area": "keyword_match", "potential_gain": 12.5},
                {"area": "structure", "potential_gain": 8.3},
                {"area": "readability", "potential_gain": 6.7}
            ]
        }
        return mock_data
    
    async def _get_keyword_optimization_insights(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze keyword optimization performance"""
        mock_data = {
            "avg_keyword_match": 78.5,
            "keyword_match_change": 15.2,
            "keyword_trend": "up",
            "top_performing_keywords": [
                {"keyword": "Python", "frequency": 18, "success_impact": 23.5},
                {"keyword": "Machine Learning", "frequency": 12, "success_impact": 19.8},
                {"keyword": "AWS", "frequency": 15, "success_impact": 17.2},
                {"keyword": "Agile", "frequency": 14, "success_impact": 12.8}
            ],
            "missing_keywords": [
                {"keyword": "Docker", "potential_impact": 15.3, "frequency_in_jobs": 8},
                {"keyword": "Kubernetes", "potential_impact": 12.7, "frequency_in_jobs": 6},
                {"keyword": "CI/CD", "potential_impact": 11.2, "frequency_in_jobs": 7}
            ],
            "industry_keyword_trends": {
                "tech": ["AI/ML", "Cloud", "DevOps", "Microservices"],
                "finance": ["Risk Management", "Compliance", "Analytics", "Fintech"],
                "healthcare": ["HIPAA", "Clinical", "EHR", "Telemedicine"]
            }
        }
        return mock_data
    
    async def _generate_success_insights(self, user_id: str, metrics_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate actionable success insights"""
        insights = [
            SuccessInsight(
                category="Template Performance",
                insight="Your Executive template generates 31% higher success rates than other templates",
                impact_score=85.2,
                recommendation="Use Executive template for senior-level positions and Modern template for tech roles",
                data_points=[{"template": "executive", "success_rate": 31.2}, {"template": "modern", "success_rate": 28.5}]
            ).__dict__,
            SuccessInsight(
                category="Keyword Optimization",
                insight="Adding 'Docker' and 'Kubernetes' keywords could improve your ATS scores by 15%",
                impact_score=78.5,
                recommendation="Include container orchestration keywords in technical resumes",
                data_points=[{"keyword": "Docker", "impact": 15.3}, {"keyword": "Kubernetes", "impact": 12.7}]
            ).__dict__,
            SuccessInsight(
                category="Application Timing",
                insight="Applications submitted on Tuesday-Thursday show 23% higher response rates",
                impact_score=72.3,
                recommendation="Focus your application efforts on mid-week submissions",
                data_points=[{"day": "Tuesday", "response_rate": 28.5}, {"day": "Wednesday", "response_rate": 31.2}]
            ).__dict__
        ]
        return insights
    
    async def _generate_personalized_recommendations(self, user_id: str, metrics_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = [
            {
                "category": "Immediate Actions",
                "priority": "high",
                "title": "Optimize for Missing Keywords",
                "description": "Add 'Docker', 'Kubernetes', and 'CI/CD' to your technical resumes",
                "expected_impact": "15% improvement in ATS scores",
                "effort": "low"
            },
            {
                "category": "Template Strategy",
                "priority": "medium",
                "title": "Leverage Executive Template",
                "description": "Use Executive template for senior roles - it shows 31% higher success rates",
                "expected_impact": "8% improvement in interview rates",
                "effort": "low"
            },
            {
                "category": "Application Strategy",
                "priority": "medium",
                "title": "Optimize Application Timing",
                "description": "Submit applications on Tuesday-Thursday for best response rates",
                "expected_impact": "23% higher response rates",
                "effort": "low"
            },
            {
                "category": "Content Enhancement",
                "priority": "low",
                "title": "Improve Readability Scores",
                "description": "Optimize sentence structure and formatting for better readability",
                "expected_impact": "6% improvement in ATS scores",
                "effort": "medium"
            }
        ]
        return recommendations
    
    async def get_success_rate_analysis(self, user_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """Detailed success rate analysis"""
        # This would integrate with application tracking data
        return {
            "overall_success_rate": 26.7,
            "industry_benchmark": 18.5,
            "performance_vs_benchmark": 44.3,  # % better than benchmark
            "success_factors": [
                {"factor": "ATS Score > 85", "success_rate": 35.2},
                {"factor": "Executive Template", "success_rate": 31.2},
                {"factor": "Heavy Mode Tailoring", "success_rate": 29.8},
                {"factor": "Cover Letter Included", "success_rate": 28.5}
            ],
            "improvement_opportunities": [
                {"opportunity": "Keyword Optimization", "potential_gain": "12%"},
                {"opportunity": "Template Selection", "potential_gain": "8%"},
                {"opportunity": "Application Timing", "potential_gain": "6%"}
            ]
        }
    
    async def export_analytics_data(self, user_id: str, format: str = "json") -> Dict[str, Any]:
        """Export analytics data for user"""
        dashboard_data = await self.get_dashboard_overview(user_id, "90d")
        
        if format == "csv":
            # Convert to CSV format
            return {"format": "csv", "data": "CSV data would be generated here"}
        else:
            return {"format": "json", "data": dashboard_data}
