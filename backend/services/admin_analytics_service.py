"""
Admin Analytics Service

This service provides comprehensive admin monitoring and analytics including:
- Subscription metrics and conversion tracking
- User behavior analytics and feature adoption
- Payment failure monitoring and system alerts
- Revenue tracking and growth analysis
- Capacity monitoring and usage pattern analysis
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import defaultdict, Counter
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text

from models.user import (
    User, Subscription, UsageTracking, PaymentHistory,
    SubscriptionTier, SubscriptionStatus, UsageType, PaymentStatus
)


@dataclass
class AlertConfig:
    """Configuration for automated alerts"""
    name: str
    threshold: float
    comparison: str  # 'greater_than', 'less_than', 'equals'
    enabled: bool = True
    notification_channels: List[str] = None


class AlertType(Enum):
    """Types of system alerts"""
    HIGH_CHURN_RATE = "high_churn_rate"
    LOW_CONVERSION_RATE = "low_conversion_rate"
    PAYMENT_FAILURE_SPIKE = "payment_failure_spike"
    SYSTEM_CAPACITY_WARNING = "system_capacity_warning"
    UNUSUAL_USAGE_PATTERN = "unusual_usage_pattern"
    REVENUE_DROP = "revenue_drop"


class AdminAnalyticsService:
    """Comprehensive admin analytics and monitoring service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Alert configurations
        self.alert_configs = {
            AlertType.HIGH_CHURN_RATE: AlertConfig(
                name="High Churn Rate",
                threshold=15.0,  # 15% monthly churn
                comparison="greater_than",
                notification_channels=["email", "slack"]
            ),
            AlertType.LOW_CONVERSION_RATE: AlertConfig(
                name="Low Conversion Rate",
                threshold=2.0,  # 2% conversion rate
                comparison="less_than",
                notification_channels=["email"]
            ),
            AlertType.PAYMENT_FAILURE_SPIKE: AlertConfig(
                name="Payment Failure Spike",
                threshold=10.0,  # 10% failure rate
                comparison="greater_than",
                notification_channels=["email", "slack", "sms"]
            ),
            AlertType.SYSTEM_CAPACITY_WARNING: AlertConfig(
                name="System Capacity Warning",
                threshold=80.0,  # 80% capacity
                comparison="greater_than",
                notification_channels=["email", "slack"]
            )
        }
        
        # Cache for real-time metrics
        self.metrics_cache = {}
        self.last_cache_update = None
    
    # Subscription Metrics and Conversion Tracking
    
    async def get_subscription_metrics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive subscription metrics for admin dashboard"""
        try:
            end_date = datetime.utcnow()
            days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
            start_date = end_date - timedelta(days=days)
            
            # Total users by tier
            tier_counts = self.db.query(
                User.subscription_tier,
                func.count(User.id).label('count')
            ).group_by(User.subscription_tier).all()
            
            # Active subscriptions
            active_subscriptions = self.db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).count()
            
            # New subscriptions in time range
            new_subscriptions = self.db.query(Subscription).filter(
                Subscription.created_at >= start_date
            ).count()
            
            # Canceled subscriptions in time range
            canceled_subscriptions = self.db.query(Subscription).filter(
                and_(
                    Subscription.status == SubscriptionStatus.CANCELED,
                    Subscription.canceled_at >= start_date
                )
            ).count()
            
            # Conversion rate calculation
            total_free_users = self.db.query(User).filter(
                User.subscription_tier == SubscriptionTier.FREE
            ).count()
            
            conversion_rate = (new_subscriptions / max(1, total_free_users)) * 100
            
            # Churn rate calculation
            churn_rate = (canceled_subscriptions / max(1, active_subscriptions)) * 100
            
            # Monthly Recurring Revenue (MRR) - assuming $9.99/month
            pro_users = self.db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.PRO,
                    User.subscription_status == SubscriptionStatus.ACTIVE
                )
            ).count()
            
            mrr = pro_users * 9.99
            
            # Growth metrics
            previous_period_start = start_date - timedelta(days=days)
            previous_new_subs = self.db.query(Subscription).filter(
                and_(
                    Subscription.created_at >= previous_period_start,
                    Subscription.created_at < start_date
                )
            ).count()
            
            growth_rate = ((new_subscriptions - previous_new_subs) / max(1, previous_new_subs)) * 100
            
            return {
                "overview": {
                    "total_users": sum(tier.count for tier in tier_counts),
                    "active_subscriptions": active_subscriptions,
                    "new_subscriptions": new_subscriptions,
                    "canceled_subscriptions": canceled_subscriptions,
                    "conversion_rate": round(conversion_rate, 2),
                    "churn_rate": round(churn_rate, 2),
                    "mrr": round(mrr, 2),
                    "growth_rate": round(growth_rate, 2)
                },
                "tier_distribution": {
                    tier.subscription_tier.value: tier.count 
                    for tier in tier_counts
                },
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting subscription metrics: {e}")
            return {"error": "Failed to generate subscription metrics"}
    
    async def get_conversion_funnel_analysis(self) -> Dict[str, Any]:
        """Analyze conversion funnel from registration to subscription"""
        try:
            # Total registered users
            total_users = self.db.query(User).count()
            
            # Users who have generated at least one resume
            active_users = self.db.query(User).filter(
                User.total_usage_count > 0
            ).count()
            
            # Users who have hit usage limits
            limit_reached_users = self.db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.FREE,
                    User.weekly_usage_count >= 5
                )
            ).count()
            
            # Users who upgraded to Pro
            pro_users = self.db.query(User).filter(
                User.subscription_tier == SubscriptionTier.PRO
            ).count()
            
            # Calculate conversion rates
            activation_rate = (active_users / max(1, total_users)) * 100
            limit_reach_rate = (limit_reached_users / max(1, active_users)) * 100
            conversion_rate = (pro_users / max(1, limit_reached_users)) * 100
            
            return {
                "funnel_stages": {
                    "registered": total_users,
                    "activated": active_users,
                    "limit_reached": limit_reached_users,
                    "converted": pro_users
                },
                "conversion_rates": {
                    "registration_to_activation": round(activation_rate, 2),
                    "activation_to_limit": round(limit_reach_rate, 2),
                    "limit_to_conversion": round(conversion_rate, 2),
                    "overall_conversion": round((pro_users / max(1, total_users)) * 100, 2)
                },
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing conversion funnel: {e}")
            return {"error": "Failed to analyze conversion funnel"}
    
    # User Behavior Analytics and Feature Adoption
    
    async def get_user_behavior_analytics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive user behavior analytics"""
        try:
            end_date = datetime.utcnow()
            days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
            start_date = end_date - timedelta(days=days)
            
            # Usage patterns by type
            usage_by_type = self.db.query(
                UsageTracking.usage_type,
                func.count(UsageTracking.id).label('count'),
                func.sum(UsageTracking.count).label('total_usage')
            ).filter(
                UsageTracking.usage_date >= start_date
            ).group_by(UsageTracking.usage_type).all()
            
            # Daily active users
            daily_active_users = self.db.query(
                func.date(UsageTracking.usage_date).label('date'),
                func.count(func.distinct(UsageTracking.user_id)).label('dau')
            ).filter(
                UsageTracking.usage_date >= start_date
            ).group_by(func.date(UsageTracking.usage_date)).all()
            
            # User retention analysis
            retention_data = await self._calculate_user_retention(start_date, end_date)
            
            # Feature adoption rates
            feature_adoption = await self._calculate_feature_adoption_rates(start_date, end_date)
            
            # User segmentation
            user_segments = await self._analyze_user_segments()
            
            return {
                "usage_patterns": {
                    usage.usage_type.value: {
                        "sessions": usage.count,
                        "total_usage": usage.total_usage
                    }
                    for usage in usage_by_type
                },
                "daily_active_users": {
                    str(dau.date): dau.dau for dau in daily_active_users
                },
                "retention": retention_data,
                "feature_adoption": feature_adoption,
                "user_segments": user_segments,
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user behavior analytics: {e}")
            return {"error": "Failed to generate user behavior analytics"}
    
    async def _calculate_user_retention(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate user retention metrics"""
        try:
            # Users who registered in the period
            new_users = self.db.query(User).filter(
                User.created_at >= start_date
            ).all()
            
            # Calculate retention for different periods
            retention_periods = [1, 7, 30]  # 1 day, 1 week, 1 month
            retention_data = {}
            
            for period in retention_periods:
                retained_users = 0
                for user in new_users:
                    # Check if user was active after the retention period
                    retention_date = user.created_at + timedelta(days=period)
                    if retention_date <= end_date:
                        activity = self.db.query(UsageTracking).filter(
                            and_(
                                UsageTracking.user_id == user.id,
                                UsageTracking.usage_date >= retention_date,
                                UsageTracking.usage_date <= retention_date + timedelta(days=1)
                            )
                        ).first()
                        
                        if activity:
                            retained_users += 1
                
                retention_rate = (retained_users / max(1, len(new_users))) * 100
                retention_data[f"day_{period}"] = {
                    "retained_users": retained_users,
                    "total_new_users": len(new_users),
                    "retention_rate": round(retention_rate, 2)
                }
            
            return retention_data
            
        except Exception as e:
            self.logger.error(f"Error calculating user retention: {e}")
            return {}
    
    async def _calculate_feature_adoption_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate feature adoption rates"""
        try:
            total_active_users = self.db.query(func.distinct(UsageTracking.user_id)).filter(
                UsageTracking.usage_date >= start_date
            ).count()
            
            # Feature usage by type
            feature_usage = self.db.query(
                UsageTracking.usage_type,
                func.count(func.distinct(UsageTracking.user_id)).label('unique_users')
            ).filter(
                UsageTracking.usage_date >= start_date
            ).group_by(UsageTracking.usage_type).all()
            
            adoption_rates = {}
            for usage in feature_usage:
                adoption_rate = (usage.unique_users / max(1, total_active_users)) * 100
                adoption_rates[usage.usage_type.value] = {
                    "unique_users": usage.unique_users,
                    "adoption_rate": round(adoption_rate, 2)
                }
            
            # Pro feature adoption (for Pro users only)
            pro_users = self.db.query(User).filter(
                User.subscription_tier == SubscriptionTier.PRO
            ).count()
            
            # Mock Pro feature usage (would track actual usage in production)
            pro_features = {
                "advanced_formatting": int(pro_users * 0.65),
                "heavy_tailoring": int(pro_users * 0.78),
                "analytics_dashboard": int(pro_users * 0.45),
                "premium_templates": int(pro_users * 0.82)
            }
            
            for feature, users in pro_features.items():
                adoption_rate = (users / max(1, pro_users)) * 100
                adoption_rates[f"pro_{feature}"] = {
                    "unique_users": users,
                    "adoption_rate": round(adoption_rate, 2)
                }
            
            return adoption_rates
            
        except Exception as e:
            self.logger.error(f"Error calculating feature adoption rates: {e}")
            return {}
    
    async def _analyze_user_segments(self) -> Dict[str, Any]:
        """Analyze user segments and behavior patterns"""
        try:
            # Segment by subscription tier
            tier_segments = self.db.query(
                User.subscription_tier,
                func.count(User.id).label('count'),
                func.avg(User.total_usage_count).label('avg_usage'),
                func.avg(func.extract('epoch', func.now() - User.created_at) / 86400).label('avg_age_days')
            ).group_by(User.subscription_tier).all()
            
            # Segment by usage level
            usage_segments = {
                "power_users": self.db.query(User).filter(User.total_usage_count >= 50).count(),
                "regular_users": self.db.query(User).filter(
                    and_(User.total_usage_count >= 10, User.total_usage_count < 50)
                ).count(),
                "light_users": self.db.query(User).filter(
                    and_(User.total_usage_count >= 1, User.total_usage_count < 10)
                ).count(),
                "inactive_users": self.db.query(User).filter(User.total_usage_count == 0).count()
            }
            
            return {
                "by_subscription_tier": {
                    segment.subscription_tier.value: {
                        "count": segment.count,
                        "avg_usage": round(float(segment.avg_usage or 0), 2),
                        "avg_age_days": round(float(segment.avg_age_days or 0), 2)
                    }
                    for segment in tier_segments
                },
                "by_usage_level": usage_segments
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user segments: {e}")
            return {}
    
    # Payment Failure Monitoring and System Alerts
    
    async def get_payment_analytics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive payment analytics and failure monitoring"""
        try:
            end_date = datetime.utcnow()
            days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
            start_date = end_date - timedelta(days=days)
            
            # Payment status distribution
            payment_status_counts = self.db.query(
                PaymentHistory.status,
                func.count(PaymentHistory.id).label('count'),
                func.sum(PaymentHistory.amount).label('total_amount')
            ).filter(
                PaymentHistory.payment_date >= start_date
            ).group_by(PaymentHistory.status).all()
            
            # Payment failure analysis
            failed_payments = self.db.query(PaymentHistory).filter(
                and_(
                    PaymentHistory.status == PaymentStatus.FAILED,
                    PaymentHistory.payment_date >= start_date
                )
            ).all()
            
            # Failure reasons analysis
            failure_reasons = Counter()
            for payment in failed_payments:
                reason = payment.failure_reason or "unknown"
                failure_reasons[reason] += 1
            
            # Calculate failure rate
            total_payments = sum(status.count for status in payment_status_counts)
            failed_count = sum(1 for status in payment_status_counts if status.status == PaymentStatus.FAILED)
            failure_rate = (failed_count / max(1, total_payments)) * 100
            
            # Revenue analysis
            successful_payments = [
                status for status in payment_status_counts 
                if status.status == PaymentStatus.SUCCEEDED
            ]
            total_revenue = sum(status.total_amount or 0 for status in successful_payments) / 100  # Convert from cents
            
            # Check for alerts
            alerts = []
            if failure_rate > self.alert_configs[AlertType.PAYMENT_FAILURE_SPIKE].threshold:
                alerts.append({
                    "type": AlertType.PAYMENT_FAILURE_SPIKE.value,
                    "severity": "high",
                    "message": f"Payment failure rate is {failure_rate:.1f}%, above threshold of {self.alert_configs[AlertType.PAYMENT_FAILURE_SPIKE].threshold}%",
                    "triggered_at": datetime.utcnow().isoformat()
                })
            
            return {
                "overview": {
                    "total_payments": total_payments,
                    "successful_payments": sum(1 for status in payment_status_counts if status.status == PaymentStatus.SUCCEEDED),
                    "failed_payments": failed_count,
                    "failure_rate": round(failure_rate, 2),
                    "total_revenue": round(total_revenue, 2)
                },
                "payment_status_distribution": {
                    status.status.value: {
                        "count": status.count,
                        "total_amount": round((status.total_amount or 0) / 100, 2)
                    }
                    for status in payment_status_counts
                },
                "failure_analysis": {
                    "failure_reasons": dict(failure_reasons),
                    "failure_rate_trend": await self._calculate_failure_rate_trend(start_date, end_date)
                },
                "alerts": alerts,
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting payment analytics: {e}")
            return {"error": "Failed to generate payment analytics"}
    
    async def _calculate_failure_rate_trend(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate payment failure rate trend over time"""
        try:
            # Group payments by day
            daily_payments = self.db.query(
                func.date(PaymentHistory.payment_date).label('date'),
                PaymentHistory.status,
                func.count(PaymentHistory.id).label('count')
            ).filter(
                PaymentHistory.payment_date >= start_date
            ).group_by(
                func.date(PaymentHistory.payment_date),
                PaymentHistory.status
            ).all()
            
            # Calculate daily failure rates
            daily_stats = defaultdict(lambda: {"total": 0, "failed": 0})
            
            for payment in daily_payments:
                date_str = str(payment.date)
                daily_stats[date_str]["total"] += payment.count
                if payment.status == PaymentStatus.FAILED:
                    daily_stats[date_str]["failed"] += payment.count
            
            # Calculate failure rates
            daily_failure_rates = {}
            for date, stats in daily_stats.items():
                failure_rate = (stats["failed"] / max(1, stats["total"])) * 100
                daily_failure_rates[date] = round(failure_rate, 2)
            
            return {
                "daily_failure_rates": daily_failure_rates,
                "trend": "increasing" if len(daily_failure_rates) > 1 and 
                        list(daily_failure_rates.values())[-1] > list(daily_failure_rates.values())[0] 
                        else "stable"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating failure rate trend: {e}")
            return {}
    
    async def check_system_alerts(self) -> List[Dict[str, Any]]:
        """Check for system alerts and anomalies"""
        try:
            alerts = []
            
            # Check subscription metrics for alerts
            metrics = await self.get_subscription_metrics("30d")
            if "overview" in metrics:
                overview = metrics["overview"]
                
                # High churn rate alert
                if overview["churn_rate"] > self.alert_configs[AlertType.HIGH_CHURN_RATE].threshold:
                    alerts.append({
                        "type": AlertType.HIGH_CHURN_RATE.value,
                        "severity": "medium",
                        "message": f"Churn rate is {overview['churn_rate']:.1f}%, above threshold of {self.alert_configs[AlertType.HIGH_CHURN_RATE].threshold}%",
                        "value": overview["churn_rate"],
                        "threshold": self.alert_configs[AlertType.HIGH_CHURN_RATE].threshold,
                        "triggered_at": datetime.utcnow().isoformat()
                    })
                
                # Low conversion rate alert
                if overview["conversion_rate"] < self.alert_configs[AlertType.LOW_CONVERSION_RATE].threshold:
                    alerts.append({
                        "type": AlertType.LOW_CONVERSION_RATE.value,
                        "severity": "medium",
                        "message": f"Conversion rate is {overview['conversion_rate']:.1f}%, below threshold of {self.alert_configs[AlertType.LOW_CONVERSION_RATE].threshold}%",
                        "value": overview["conversion_rate"],
                        "threshold": self.alert_configs[AlertType.LOW_CONVERSION_RATE].threshold,
                        "triggered_at": datetime.utcnow().isoformat()
                    })
            
            # Check payment failure rates
            payment_analytics = await self.get_payment_analytics("7d")
            if "overview" in payment_analytics:
                failure_rate = payment_analytics["overview"]["failure_rate"]
                if failure_rate > self.alert_configs[AlertType.PAYMENT_FAILURE_SPIKE].threshold:
                    alerts.append({
                        "type": AlertType.PAYMENT_FAILURE_SPIKE.value,
                        "severity": "high",
                        "message": f"Payment failure rate is {failure_rate:.1f}%, above threshold of {self.alert_configs[AlertType.PAYMENT_FAILURE_SPIKE].threshold}%",
                        "value": failure_rate,
                        "threshold": self.alert_configs[AlertType.PAYMENT_FAILURE_SPIKE].threshold,
                        "triggered_at": datetime.utcnow().isoformat()
                    })
            
            # Check system capacity (mock implementation)
            system_capacity = await self._check_system_capacity()
            if system_capacity["usage_percentage"] > self.alert_configs[AlertType.SYSTEM_CAPACITY_WARNING].threshold:
                alerts.append({
                    "type": AlertType.SYSTEM_CAPACITY_WARNING.value,
                    "severity": "medium",
                    "message": f"System capacity is at {system_capacity['usage_percentage']:.1f}%, above threshold of {self.alert_configs[AlertType.SYSTEM_CAPACITY_WARNING].threshold}%",
                    "value": system_capacity["usage_percentage"],
                    "threshold": self.alert_configs[AlertType.SYSTEM_CAPACITY_WARNING].threshold,
                    "triggered_at": datetime.utcnow().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking system alerts: {e}")
            return []
    
    async def _check_system_capacity(self) -> Dict[str, Any]:
        """Check system capacity and resource usage"""
        try:
            # Mock system capacity check (would integrate with actual monitoring in production)
            import random
            
            # Simulate capacity metrics
            cpu_usage = random.uniform(30, 95)
            memory_usage = random.uniform(40, 90)
            disk_usage = random.uniform(20, 85)
            
            # Calculate overall usage percentage
            usage_percentage = (cpu_usage + memory_usage + disk_usage) / 3
            
            return {
                "cpu_usage": round(cpu_usage, 1),
                "memory_usage": round(memory_usage, 1),
                "disk_usage": round(disk_usage, 1),
                "usage_percentage": round(usage_percentage, 1),
                "status": "warning" if usage_percentage > 80 else "normal",
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking system capacity: {e}")
            return {"usage_percentage": 0, "status": "error"}
    
    # Revenue Tracking and Growth Analysis
    
    async def get_revenue_analytics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive revenue analytics and growth tracking"""
        try:
            end_date = datetime.utcnow()
            days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
            start_date = end_date - timedelta(days=days)
            
            # Current MRR calculation
            active_pro_users = self.db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.PRO,
                    User.subscription_status == SubscriptionStatus.ACTIVE
                )
            ).count()
            
            current_mrr = active_pro_users * 9.99
            
            # Historical revenue from payments
            successful_payments = self.db.query(
                func.date(PaymentHistory.payment_date).label('date'),
                func.sum(PaymentHistory.amount).label('daily_revenue')
            ).filter(
                and_(
                    PaymentHistory.status == PaymentStatus.SUCCEEDED,
                    PaymentHistory.payment_date >= start_date
                )
            ).group_by(func.date(PaymentHistory.payment_date)).all()
            
            # Calculate total revenue for period
            total_revenue = sum(payment.daily_revenue or 0 for payment in successful_payments) / 100
            
            # Previous period comparison
            previous_start = start_date - timedelta(days=days)
            previous_payments = self.db.query(
                func.sum(PaymentHistory.amount).label('total')
            ).filter(
                and_(
                    PaymentHistory.status == PaymentStatus.SUCCEEDED,
                    PaymentHistory.payment_date >= previous_start,
                    PaymentHistory.payment_date < start_date
                )
            ).scalar() or 0
            
            previous_revenue = previous_payments / 100
            revenue_growth = ((total_revenue - previous_revenue) / max(1, previous_revenue)) * 100
            
            # Revenue per user metrics
            total_users = self.db.query(User).count()
            arpu = total_revenue / max(1, total_users)  # Average Revenue Per User
            
            # Churn impact on revenue
            churned_users = self.db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.FREE,
                    User.subscription_status == SubscriptionStatus.CANCELED
                )
            ).count()
            
            churn_revenue_impact = churned_users * 9.99
            
            return {
                "overview": {
                    "current_mrr": round(current_mrr, 2),
                    "total_revenue": round(total_revenue, 2),
                    "revenue_growth": round(revenue_growth, 2),
                    "arpu": round(arpu, 2),
                    "churn_revenue_impact": round(churn_revenue_impact, 2)
                },
                "daily_revenue": {
                    str(payment.date): round((payment.daily_revenue or 0) / 100, 2)
                    for payment in successful_payments
                },
                "projections": {
                    "next_month_mrr": round(current_mrr * (1 + revenue_growth/100), 2),
                    "annual_run_rate": round(current_mrr * 12, 2)
                },
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting revenue analytics: {e}")
            return {"error": "Failed to generate revenue analytics"}
    
    # Capacity Monitoring and Usage Pattern Analysis
    
    async def get_capacity_analytics(self) -> Dict[str, Any]:
        """Get system capacity and usage pattern analytics"""
        try:
            # Current usage statistics
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=7)
            
            # Daily usage patterns
            daily_usage = self.db.query(
                func.date(UsageTracking.usage_date).label('date'),
                func.count(UsageTracking.id).label('sessions'),
                func.count(func.distinct(UsageTracking.user_id)).label('unique_users')
            ).filter(
                UsageTracking.usage_date >= week_start
            ).group_by(func.date(UsageTracking.usage_date)).all()
            
            # Peak usage analysis
            hourly_usage = self.db.query(
                func.extract('hour', UsageTracking.usage_date).label('hour'),
                func.count(UsageTracking.id).label('sessions')
            ).filter(
                UsageTracking.usage_date >= week_start
            ).group_by(func.extract('hour', UsageTracking.usage_date)).all()
            
            # Usage by feature type
            feature_usage = self.db.query(
                UsageTracking.usage_type,
                func.count(UsageTracking.id).label('sessions'),
                func.avg(UsageTracking.count).label('avg_count')
            ).filter(
                UsageTracking.usage_date >= week_start
            ).group_by(UsageTracking.usage_type).all()
            
            # System capacity metrics
            system_capacity = await self._check_system_capacity()
            
            # Usage predictions
            avg_daily_sessions = sum(usage.sessions for usage in daily_usage) / max(1, len(daily_usage))
            predicted_peak = avg_daily_sessions * 1.5  # Assume 50% peak capacity needed
            
            return {
                "current_usage": {
                    "daily_sessions": {
                        str(usage.date): {
                            "sessions": usage.sessions,
                            "unique_users": usage.unique_users
                        }
                        for usage in daily_usage
                    },
                    "peak_hours": {
                        int(usage.hour): usage.sessions
                        for usage in hourly_usage
                    },
                    "feature_usage": {
                        usage.usage_type.value: {
                            "sessions": usage.sessions,
                            "avg_count": round(float(usage.avg_count or 0), 2)
                        }
                        for usage in feature_usage
                    }
                },
                "system_capacity": system_capacity,
                "predictions": {
                    "avg_daily_sessions": round(avg_daily_sessions, 1),
                    "predicted_peak_sessions": round(predicted_peak, 1),
                    "capacity_utilization": round((avg_daily_sessions / max(1, predicted_peak)) * 100, 1)
                },
                "recommendations": await self._generate_capacity_recommendations(system_capacity, avg_daily_sessions),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting capacity analytics: {e}")
            return {"error": "Failed to generate capacity analytics"}
    
    async def _generate_capacity_recommendations(self, system_capacity: Dict, avg_sessions: float) -> List[str]:
        """Generate capacity and performance recommendations"""
        recommendations = []
        
        if system_capacity["usage_percentage"] > 80:
            recommendations.append("Consider scaling up system resources - usage is above 80%")
        
        if system_capacity["cpu_usage"] > 85:
            recommendations.append("CPU usage is high - consider optimizing processing algorithms")
        
        if system_capacity["memory_usage"] > 85:
            recommendations.append("Memory usage is high - review caching strategies")
        
        if avg_sessions > 1000:
            recommendations.append("High session volume - consider implementing load balancing")
        
        if not recommendations:
            recommendations.append("System capacity is within normal parameters")
        
        return recommendations
    
    # Comprehensive Admin Dashboard
    
    async def get_admin_dashboard(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get comprehensive admin dashboard with all key metrics"""
        try:
            # Gather all analytics data
            subscription_metrics = await self.get_subscription_metrics(time_range)
            user_behavior = await self.get_user_behavior_analytics(time_range)
            payment_analytics = await self.get_payment_analytics(time_range)
            revenue_analytics = await self.get_revenue_analytics(time_range)
            capacity_analytics = await self.get_capacity_analytics()
            system_alerts = await self.check_system_alerts()
            conversion_funnel = await self.get_conversion_funnel_analysis()
            
            return {
                "dashboard_overview": {
                    "total_users": subscription_metrics.get("overview", {}).get("total_users", 0),
                    "active_subscriptions": subscription_metrics.get("overview", {}).get("active_subscriptions", 0),
                    "mrr": revenue_analytics.get("overview", {}).get("current_mrr", 0),
                    "churn_rate": subscription_metrics.get("overview", {}).get("churn_rate", 0),
                    "conversion_rate": subscription_metrics.get("overview", {}).get("conversion_rate", 0),
                    "system_health": "healthy" if len(system_alerts) == 0 else "warning"
                },
                "subscription_metrics": subscription_metrics,
                "user_behavior": user_behavior,
                "payment_analytics": payment_analytics,
                "revenue_analytics": revenue_analytics,
                "capacity_analytics": capacity_analytics,
                "conversion_funnel": conversion_funnel,
                "alerts": system_alerts,
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating admin dashboard: {e}")
            return {"error": "Failed to generate admin dashboard"}