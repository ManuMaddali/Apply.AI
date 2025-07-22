"""
Analytics Service for Pro Users

This service provides comprehensive analytics and insights for Pro subscribers,
including success rates, keyword optimization scores, and performance tracking.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import defaultdict, Counter

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from models.user import User
from services.subscription_service import SubscriptionService


class AnalyticsEventType(Enum):
    """Types of analytics events to track"""
    RESUME_GENERATED = "resume_generated"
    COVER_LETTER_GENERATED = "cover_letter_generated"
    BULK_PROCESSING = "bulk_processing"
    ADVANCED_FORMATTING = "advanced_formatting"
    JOB_APPLICATION = "job_application"
    TEMPLATE_USAGE = "template_usage"
    KEYWORD_OPTIMIZATION = "keyword_optimization"


class AnalyticsMetric(Enum):
    """Analytics metrics to calculate"""
    SUCCESS_RATE = "success_rate"
    KEYWORD_MATCH_SCORE = "keyword_match_score"
    TEMPLATE_EFFECTIVENESS = "template_effectiveness"
    USAGE_FREQUENCY = "usage_frequency"
    FEATURE_ADOPTION = "feature_adoption"
    PERFORMANCE_TREND = "performance_trend"


class AnalyticsService:
    """Comprehensive analytics service for Pro users"""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.logger = logging.getLogger(__name__)
        
        # In-memory storage for real-time analytics (would use Redis in production)
        self.analytics_cache = defaultdict(list)
        self.metrics_cache = {}
        
    async def track_event(
        self,
        user_id: str,
        event_type: AnalyticsEventType,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an analytics event for a user
        
        Args:
            user_id: User ID
            event_type: Type of event being tracked
            event_data: Event-specific data
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Verify user exists and has Pro subscription for detailed analytics
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Create analytics event record
            event_record = {
                "user_id": user_id,
                "event_type": event_type.value,
                "event_data": event_data,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
                "subscription_tier": user.subscription_tier
            }
            
            # Store in cache for real-time access
            self.analytics_cache[user_id].append(event_record)
            
            # Keep only last 1000 events per user in cache
            if len(self.analytics_cache[user_id]) > 1000:
                self.analytics_cache[user_id] = self.analytics_cache[user_id][-1000:]
            
            # Log event for persistence (would save to database in production)
            self.logger.info(f"Analytics event tracked: {json.dumps(event_record)}")
            
            # Update real-time metrics
            await self._update_real_time_metrics(user_id, event_type, event_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track analytics event: {str(e)}")
            return False
    
    async def get_user_analytics_dashboard(
        self,
        user_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics dashboard data for Pro user
        
        Args:
            user_id: User ID
            time_range: Time range for analytics (7d, 30d, 90d, 1y)
            
        Returns:
            Dict containing dashboard analytics
        """
        try:
            # Verify Pro subscription
            can_access = await self.subscription_service.can_use_feature(user_id, "analytics")
            if not can_access:
                return {"error": "Analytics requires Pro subscription"}
            
            # Calculate time range
            end_date = datetime.utcnow()
            days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
            start_date = end_date - timedelta(days=days)
            
            # Get user events in time range
            user_events = self._get_user_events_in_range(user_id, start_date, end_date)
            
            # Calculate key metrics
            dashboard_data = {
                "overview": await self._calculate_overview_metrics(user_events, time_range),
                "success_rates": await self._calculate_success_rates(user_events),
                "keyword_optimization": await self._calculate_keyword_optimization(user_events),
                "template_performance": await self._calculate_template_performance(user_events),
                "usage_trends": await self._calculate_usage_trends(user_events, start_date, end_date),
                "feature_adoption": await self._calculate_feature_adoption(user_events),
                "recommendations": await self._generate_recommendations(user_id, user_events),
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics dashboard: {str(e)}")
            return {"error": "Failed to generate analytics dashboard"}
    
    async def get_keyword_optimization_score(
        self,
        user_id: str,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Calculate keyword optimization score for a resume against job description
        
        Args:
            user_id: User ID
            resume_text: Resume content
            job_description: Job posting description
            
        Returns:
            Dict containing optimization score and recommendations
        """
        try:
            # Verify Pro subscription
            can_access = await self.subscription_service.can_use_feature(user_id, "analytics")
            if not can_access:
                return {"error": "Keyword optimization requires Pro subscription"}
            
            # Extract keywords from job description
            job_keywords = self._extract_keywords(job_description)
            resume_keywords = self._extract_keywords(resume_text)
            
            # Calculate match score
            matched_keywords = set(job_keywords) & set(resume_keywords)
            match_score = len(matched_keywords) / len(job_keywords) if job_keywords else 0
            
            # Identify missing critical keywords
            missing_keywords = set(job_keywords) - set(resume_keywords)
            
            # Calculate keyword density and frequency
            keyword_analysis = self._analyze_keyword_usage(resume_text, job_keywords)
            
            # Track this analysis
            await self.track_event(
                user_id=user_id,
                event_type=AnalyticsEventType.KEYWORD_OPTIMIZATION,
                event_data={
                    "match_score": match_score,
                    "matched_keywords": list(matched_keywords),
                    "missing_keywords": list(missing_keywords),
                    "total_job_keywords": len(job_keywords)
                }
            )
            
            return {
                "optimization_score": round(match_score * 100, 1),
                "grade": self._get_optimization_grade(match_score),
                "matched_keywords": list(matched_keywords),
                "missing_keywords": list(missing_keywords),
                "keyword_analysis": keyword_analysis,
                "recommendations": self._generate_keyword_recommendations(
                    match_score, missing_keywords, keyword_analysis
                ),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Keyword optimization analysis failed: {str(e)}")
            return {"error": "Failed to analyze keyword optimization"}
    
    async def get_success_rate_analytics(
        self,
        user_id: str,
        metric_type: str = "overall"
    ) -> Dict[str, Any]:
        """
        Get detailed success rate analytics for user
        
        Args:
            user_id: User ID
            metric_type: Type of success metric (overall, by_template, by_industry)
            
        Returns:
            Dict containing success rate analytics
        """
        try:
            # Verify Pro subscription
            can_access = await self.subscription_service.can_use_feature(user_id, "analytics")
            if not can_access:
                return {"error": "Success rate analytics requires Pro subscription"}
            
            user_events = self.analytics_cache.get(user_id, [])
            
            if metric_type == "overall":
                return await self._calculate_overall_success_rate(user_events)
            elif metric_type == "by_template":
                return await self._calculate_success_by_template(user_events)
            elif metric_type == "by_industry":
                return await self._calculate_success_by_industry(user_events)
            else:
                return {"error": "Invalid metric type"}
                
        except Exception as e:
            self.logger.error(f"Success rate analytics failed: {str(e)}")
            return {"error": "Failed to generate success rate analytics"}
    
    def _get_user_events_in_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get user events within specified date range"""
        user_events = self.analytics_cache.get(user_id, [])
        
        filtered_events = []
        for event in user_events:
            event_time = datetime.fromisoformat(event["timestamp"])
            if start_date <= event_time <= end_date:
                filtered_events.append(event)
        
        return filtered_events
    
    async def _calculate_overview_metrics(
        self,
        events: List[Dict],
        time_range: str
    ) -> Dict[str, Any]:
        """Calculate overview metrics for dashboard"""
        total_resumes = len([e for e in events if e["event_type"] == "resume_generated"])
        total_cover_letters = len([e for e in events if e["event_type"] == "cover_letter_generated"])
        total_applications = len([e for e in events if e["event_type"] == "job_application"])
        
        # Calculate success rate (mock calculation)
        success_rate = 0.75 if total_applications > 0 else 0
        
        return {
            "total_resumes_generated": total_resumes,
            "total_cover_letters_generated": total_cover_letters,
            "total_applications": total_applications,
            "overall_success_rate": round(success_rate * 100, 1),
            "time_range": time_range
        }
    
    async def _calculate_success_rates(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate various success rate metrics"""
        # Mock success rate calculations (would use real data in production)
        return {
            "resume_success_rate": 78.5,
            "cover_letter_success_rate": 82.3,
            "template_success_rates": {
                "executive": 85.2,
                "technical": 79.8,
                "creative": 81.5,
                "consulting": 83.1
            },
            "trend": "increasing"
        }
    
    async def _calculate_keyword_optimization(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate keyword optimization metrics"""
        keyword_events = [e for e in events if e["event_type"] == "keyword_optimization"]
        
        if not keyword_events:
            return {"average_score": 0, "trend": "no_data"}
        
        scores = [e["event_data"]["match_score"] * 100 for e in keyword_events]
        average_score = sum(scores) / len(scores)
        
        return {
            "average_optimization_score": round(average_score, 1),
            "best_score": round(max(scores), 1),
            "recent_scores": scores[-10:],  # Last 10 scores
            "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
        }
    
    async def _calculate_template_performance(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate template performance metrics"""
        template_usage = Counter()
        template_success = defaultdict(list)
        
        for event in events:
            if event["event_type"] == "template_usage":
                template = event["event_data"].get("template", "unknown")
                template_usage[template] += 1
                
                # Mock success rate for each template
                success_rate = 0.8 + (hash(template) % 20) / 100  # Mock calculation
                template_success[template].append(success_rate)
        
        performance_data = {}
        for template, usage_count in template_usage.items():
            avg_success = sum(template_success[template]) / len(template_success[template])
            performance_data[template] = {
                "usage_count": usage_count,
                "success_rate": round(avg_success * 100, 1),
                "effectiveness_score": round((usage_count * avg_success), 1)
            }
        
        return performance_data
    
    async def _calculate_usage_trends(
        self,
        events: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate usage trends over time"""
        # Group events by day
        daily_usage = defaultdict(int)
        
        for event in events:
            event_date = datetime.fromisoformat(event["timestamp"]).date()
            daily_usage[event_date.isoformat()] += 1
        
        # Fill in missing dates with 0
        current_date = start_date.date()
        while current_date <= end_date.date():
            if current_date.isoformat() not in daily_usage:
                daily_usage[current_date.isoformat()] = 0
            current_date += timedelta(days=1)
        
        # Sort by date
        sorted_usage = sorted(daily_usage.items())
        
        return {
            "daily_usage": dict(sorted_usage),
            "peak_usage_day": max(sorted_usage, key=lambda x: x[1])[0] if sorted_usage else None,
            "average_daily_usage": sum(daily_usage.values()) / len(daily_usage) if daily_usage else 0
        }
    
    async def _calculate_feature_adoption(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate feature adoption metrics"""
        feature_usage = Counter()
        
        for event in events:
            event_type = event["event_type"]
            feature_usage[event_type] += 1
        
        total_events = sum(feature_usage.values())
        
        adoption_rates = {}
        for feature, count in feature_usage.items():
            adoption_rates[feature] = {
                "usage_count": count,
                "adoption_rate": round((count / total_events) * 100, 1) if total_events > 0 else 0
            }
        
        return adoption_rates
    
    async def _generate_recommendations(
        self,
        user_id: str,
        events: List[Dict]
    ) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on analytics"""
        recommendations = []
        
        # Analyze usage patterns
        event_types = [e["event_type"] for e in events]
        
        # Recommendation logic
        if "cover_letter_generated" not in event_types:
            recommendations.append({
                "type": "feature_suggestion",
                "title": "Try Cover Letters",
                "description": "Boost your applications with AI-generated cover letters",
                "action": "Generate your first cover letter"
            })
        
        if "advanced_formatting" not in event_types:
            recommendations.append({
                "type": "feature_suggestion",
                "title": "Advanced Formatting",
                "description": "Stand out with professional formatting options",
                "action": "Explore formatting templates"
            })
        
        # Keyword optimization recommendation
        keyword_events = [e for e in events if e["event_type"] == "keyword_optimization"]
        if keyword_events:
            avg_score = sum(e["event_data"]["match_score"] for e in keyword_events) / len(keyword_events)
            if avg_score < 0.7:
                recommendations.append({
                    "type": "improvement",
                    "title": "Improve Keyword Optimization",
                    "description": f"Your average keyword match is {avg_score*100:.1f}%. Aim for 80%+",
                    "action": "Review keyword suggestions"
                })
        
        return recommendations
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified implementation)"""
        # This is a simplified implementation
        # In production, would use NLP libraries like spaCy or NLTK
        import re
        
        # Remove common words and extract meaningful terms
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        # Extract words (2+ characters, alphanumeric)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        # Filter out common words and return unique keywords
        keywords = list(set(word for word in words if word not in common_words))
        
        return keywords[:50]  # Limit to top 50 keywords
    
    def _analyze_keyword_usage(self, resume_text: str, job_keywords: List[str]) -> Dict[str, Any]:
        """Analyze how keywords are used in the resume"""
        keyword_density = {}
        resume_lower = resume_text.lower()
        
        for keyword in job_keywords:
            count = resume_lower.count(keyword.lower())
            density = count / len(resume_text.split()) if resume_text else 0
            keyword_density[keyword] = {
                "count": count,
                "density": round(density * 100, 2)
            }
        
        return keyword_density
    
    def _get_optimization_grade(self, score: float) -> str:
        """Get letter grade for optimization score"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B+"
        elif score >= 0.6:
            return "B"
        elif score >= 0.5:
            return "C+"
        elif score >= 0.4:
            return "C"
        else:
            return "D"
    
    def _generate_keyword_recommendations(
        self,
        match_score: float,
        missing_keywords: set,
        keyword_analysis: Dict
    ) -> List[str]:
        """Generate keyword optimization recommendations"""
        recommendations = []
        
        if match_score < 0.6:
            recommendations.append("Your keyword match is below 60%. Consider adding more relevant keywords.")
        
        if missing_keywords:
            top_missing = list(missing_keywords)[:5]
            recommendations.append(f"Consider adding these keywords: {', '.join(top_missing)}")
        
        # Check for keyword density
        low_density_keywords = [
            kw for kw, data in keyword_analysis.items()
            if data["count"] == 1 and kw in missing_keywords
        ]
        
        if low_density_keywords:
            recommendations.append("Some keywords appear only once. Consider using them more naturally throughout your resume.")
        
        return recommendations
    
    async def _update_real_time_metrics(
        self,
        user_id: str,
        event_type: AnalyticsEventType,
        event_data: Dict
    ):
        """Update real-time metrics cache"""
        try:
            cache_key = f"metrics_{user_id}"
            
            if cache_key not in self.metrics_cache:
                self.metrics_cache[cache_key] = {
                    "total_events": 0,
                    "last_activity": None,
                    "feature_usage": defaultdict(int)
                }
            
            # Update metrics
            self.metrics_cache[cache_key]["total_events"] += 1
            self.metrics_cache[cache_key]["last_activity"] = datetime.utcnow().isoformat()
            self.metrics_cache[cache_key]["feature_usage"][event_type.value] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to update real-time metrics: {str(e)}")
    
    async def _calculate_overall_success_rate(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate overall success rate metrics"""
        # Mock implementation - would use real success tracking in production
        return {
            "overall_rate": 76.8,
            "trend": "increasing",
            "benchmark": 65.0,
            "performance": "above_average"
        }
    
    async def _calculate_success_by_template(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate success rates by template"""
        # Mock implementation
        return {
            "executive": {"rate": 85.2, "applications": 23},
            "technical": {"rate": 79.8, "applications": 45},
            "creative": {"rate": 81.5, "applications": 18},
            "consulting": {"rate": 83.1, "applications": 31}
        }
    
    async def _calculate_success_by_industry(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate success rates by industry"""
        # Mock implementation
        return {
            "technology": {"rate": 82.1, "applications": 67},
            "finance": {"rate": 78.9, "applications": 34},
            "healthcare": {"rate": 80.5, "applications": 28},
            "consulting": {"rate": 84.2, "applications": 19}
        }
