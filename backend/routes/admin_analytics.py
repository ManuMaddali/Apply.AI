"""
Admin Analytics API Routes

This module provides admin-only analytics endpoints for monitoring and managing
the subscription service, including metrics, alerts, and system health monitoring.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import get_db
from services.admin_analytics_service import AdminAnalyticsService, AlertType
from utils.auth import get_current_user, require_admin_access
from models.user import User, UsageTracking
from utils.rate_limiter import limiter


# Initialize router and security
router = APIRouter(prefix="/api/admin/analytics", tags=["admin-analytics"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class AlertConfigRequest(BaseModel):
    alert_type: str = Field(..., description="Type of alert to configure")
    threshold: float = Field(..., description="Alert threshold value")
    enabled: bool = Field(True, description="Whether alert is enabled")
    notification_channels: List[str] = Field(default=["email"], description="Notification channels")


class SystemHealthResponse(BaseModel):
    status: str
    alerts: List[Dict]
    metrics: Dict
    timestamp: str


# Admin Dashboard Endpoints

@router.get("/dashboard")
@limiter.limit("10/minute")
async def get_admin_dashboard(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive admin dashboard with all key metrics
    
    **Admin Only**: Requires admin privileges
    
    **Time Ranges:**
    - 7d: Last 7 days
    - 30d: Last 30 days (default)
    - 90d: Last 90 days
    - 1y: Last year
    
    **Returns:**
    - Dashboard overview with key KPIs
    - Subscription metrics and trends
    - User behavior analytics
    - Payment and revenue analytics
    - System capacity and health
    - Active alerts and recommendations
    """
    try:
        # Verify admin access
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        dashboard_data = await admin_service.get_admin_dashboard(time_range)
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data["error"])
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate admin dashboard")


@router.get("/subscription-metrics")
@limiter.limit("20/minute")
async def get_subscription_metrics(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed subscription metrics and conversion tracking
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Total users by subscription tier
    - New subscriptions and cancellations
    - Conversion and churn rates
    - Monthly Recurring Revenue (MRR)
    - Growth metrics and trends
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        metrics = await admin_service.get_subscription_metrics(time_range)
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscription metrics")


@router.get("/conversion-funnel")
@limiter.limit("20/minute")
async def get_conversion_funnel_analysis(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversion funnel analysis from registration to subscription
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Funnel stages (registered → activated → limit reached → converted)
    - Conversion rates at each stage
    - Drop-off analysis and optimization opportunities
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        funnel_data = await admin_service.get_conversion_funnel_analysis()
        
        if "error" in funnel_data:
            raise HTTPException(status_code=500, detail=funnel_data["error"])
        
        return funnel_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion funnel analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze conversion funnel")


@router.get("/user-behavior")
@limiter.limit("20/minute")
async def get_user_behavior_analytics(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive user behavior analytics and feature adoption metrics
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Usage patterns by feature type
    - Daily active users (DAU)
    - User retention analysis
    - Feature adoption rates
    - User segmentation analysis
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        behavior_data = await admin_service.get_user_behavior_analytics(time_range)
        
        if "error" in behavior_data:
            raise HTTPException(status_code=500, detail=behavior_data["error"])
        
        return behavior_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User behavior analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user behavior analytics")


@router.get("/payment-analytics")
@limiter.limit("20/minute")
async def get_payment_analytics(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment analytics and failure monitoring
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Payment status distribution
    - Payment failure rates and trends
    - Failure reason analysis
    - Revenue impact of failures
    - Payment method performance
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        payment_data = await admin_service.get_payment_analytics(time_range)
        
        if "error" in payment_data:
            raise HTTPException(status_code=500, detail=payment_data["error"])
        
        return payment_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get payment analytics")


@router.get("/revenue-analytics")
@limiter.limit("20/minute")
async def get_revenue_analytics(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue analytics and growth tracking
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Monthly Recurring Revenue (MRR)
    - Revenue growth trends
    - Average Revenue Per User (ARPU)
    - Revenue projections
    - Churn impact on revenue
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        revenue_data = await admin_service.get_revenue_analytics(time_range)
        
        if "error" in revenue_data:
            raise HTTPException(status_code=500, detail=revenue_data["error"])
        
        return revenue_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revenue analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get revenue analytics")


@router.get("/capacity-analytics")
@limiter.limit("20/minute")
async def get_capacity_analytics(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system capacity and usage pattern analytics
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Current system usage patterns
    - Peak usage analysis
    - System capacity metrics
    - Usage predictions
    - Capacity recommendations
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        capacity_data = await admin_service.get_capacity_analytics()
        
        if "error" in capacity_data:
            raise HTTPException(status_code=500, detail=capacity_data["error"])
        
        return capacity_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Capacity analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capacity analytics")


# System Health and Alerts

@router.get("/system-health")
@limiter.limit("30/minute")
async def get_system_health(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current system health status and active alerts
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Overall system health status
    - Active alerts and their severity
    - System capacity metrics
    - Recent performance indicators
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        
        # Get system alerts
        alerts = await admin_service.check_system_alerts()
        
        # Get capacity metrics
        capacity = await admin_service.get_capacity_analytics()
        
        # Determine overall health status
        if any(alert["severity"] == "high" for alert in alerts):
            status = "critical"
        elif any(alert["severity"] == "medium" for alert in alerts):
            status = "warning"
        elif alerts:
            status = "attention"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "alerts": alerts,
            "alert_count": len(alerts),
            "system_capacity": capacity.get("system_capacity", {}),
            "recommendations": capacity.get("recommendations", []),
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check system health")


@router.get("/alerts")
@limiter.limit("30/minute")
async def get_system_alerts(
    request: Request,
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system alerts with optional severity filtering
    
    **Admin Only**: Requires admin privileges
    
    **Query Parameters:**
    - severity: Filter alerts by severity level (low, medium, high, critical)
    
    **Returns:**
    - List of active system alerts
    - Alert details and recommendations
    - Triggered timestamps and thresholds
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        alerts = await admin_service.check_system_alerts()
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert.get("severity") == severity]
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "severity_filter": severity,
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system alerts")


# Export and Reporting

@router.get("/export")
@limiter.limit("5/minute")
async def export_admin_analytics(
    request: Request,
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    format: str = Query("json", regex="^(json|csv)$"),
    include_sections: str = Query("all", description="Comma-separated list of sections to include"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export comprehensive admin analytics data
    
    **Admin Only**: Requires admin privileges
    
    **Query Parameters:**
    - time_range: Time range for analytics (7d, 30d, 90d, 1y)
    - format: Export format (json, csv)
    - include_sections: Sections to include (all, subscription, user_behavior, payment, revenue, capacity)
    
    **Returns:**
    - Comprehensive analytics data in requested format
    - Export metadata and timestamps
    
    **Rate Limited**: 5 requests per minute due to resource intensity
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        
        # Parse sections to include
        if include_sections == "all":
            sections = ["subscription", "user_behavior", "payment", "revenue", "capacity"]
        else:
            sections = [s.strip() for s in include_sections.split(",")]
        
        # Gather requested data
        export_data = {
            "export_info": {
                "exported_by": current_user.email,
                "export_format": format,
                "time_range": time_range,
                "sections_included": sections,
                "export_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if "subscription" in sections:
            export_data["subscription_metrics"] = await admin_service.get_subscription_metrics(time_range)
        
        if "user_behavior" in sections:
            export_data["user_behavior"] = await admin_service.get_user_behavior_analytics(time_range)
        
        if "payment" in sections:
            export_data["payment_analytics"] = await admin_service.get_payment_analytics(time_range)
        
        if "revenue" in sections:
            export_data["revenue_analytics"] = await admin_service.get_revenue_analytics(time_range)
        
        if "capacity" in sections:
            export_data["capacity_analytics"] = await admin_service.get_capacity_analytics()
        
        # Add conversion funnel analysis
        export_data["conversion_funnel"] = await admin_service.get_conversion_funnel_analysis()
        
        # Add current alerts
        export_data["system_alerts"] = await admin_service.check_system_alerts()
        
        if format == "csv":
            # In a real implementation, would convert to CSV format
            # For now, return JSON with CSV note
            export_data["note"] = "CSV export would be implemented with pandas or similar library"
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin analytics export error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export admin analytics")


# Real-time Monitoring

@router.get("/real-time-metrics")
@limiter.limit("60/minute")
async def get_real_time_metrics(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time system metrics for monitoring dashboard
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - Current active users
    - Real-time usage statistics
    - System performance metrics
    - Recent activity indicators
    
    **High Rate Limit**: 60 requests per minute for real-time monitoring
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        
        # Get current day metrics
        today = datetime.utcnow().date()
        
        # Current active sessions (mock - would track real sessions in production)
        current_sessions = 42  # Mock value
        
        # Today's usage
        today_usage = db.query(UsageTracking).filter(
            func.date(UsageTracking.usage_date) == today
        ).count()
        
        # System capacity
        capacity = await admin_service._check_system_capacity()
        
        # Recent alerts
        alerts = await admin_service.check_system_alerts()
        recent_alerts = [alert for alert in alerts if alert.get("severity") in ["high", "critical"]]
        
        return {
            "current_metrics": {
                "active_sessions": current_sessions,
                "today_usage_count": today_usage,
                "system_capacity": capacity["usage_percentage"],
                "critical_alerts": len(recent_alerts)
            },
            "system_status": {
                "cpu_usage": capacity["cpu_usage"],
                "memory_usage": capacity["memory_usage"],
                "disk_usage": capacity["disk_usage"],
                "overall_health": capacity["status"]
            },
            "recent_alerts": recent_alerts[:5],  # Last 5 critical alerts
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Real-time metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get real-time metrics")


# Configuration and Management

@router.post("/configure-alert")
@limiter.limit("10/minute")
async def configure_alert(
    request: Request,
    alert_config: AlertConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configure alert thresholds and notification settings
    
    **Admin Only**: Requires admin privileges
    
    **Request Body:**
    ```json
    {
        "alert_type": "high_churn_rate",
        "threshold": 15.0,
        "enabled": true,
        "notification_channels": ["email", "slack"]
    }
    ```
    
    **Supported Alert Types:**
    - high_churn_rate
    - low_conversion_rate
    - payment_failure_spike
    - system_capacity_warning
    """
    try:
        require_admin_access(current_user)
        
        # Validate alert type
        try:
            alert_type = AlertType(alert_config.alert_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid alert type: {alert_config.alert_type}")
        
        admin_service = AdminAnalyticsService(db)
        
        # Update alert configuration
        if alert_type in admin_service.alert_configs:
            config = admin_service.alert_configs[alert_type]
            config.threshold = alert_config.threshold
            config.enabled = alert_config.enabled
            config.notification_channels = alert_config.notification_channels
            
            logger.info(f"Alert configuration updated by {current_user.email}: {alert_config.alert_type}")
            
            return {
                "success": True,
                "message": f"Alert configuration updated for {alert_config.alert_type}",
                "configuration": {
                    "alert_type": alert_config.alert_type,
                    "threshold": alert_config.threshold,
                    "enabled": alert_config.enabled,
                    "notification_channels": alert_config.notification_channels
                },
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alert type not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alert configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to configure alert")


@router.get("/alert-configurations")
@limiter.limit("20/minute")
async def get_alert_configurations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current alert configurations
    
    **Admin Only**: Requires admin privileges
    
    **Returns:**
    - All configured alert types and their settings
    - Threshold values and notification channels
    - Alert status (enabled/disabled)
    """
    try:
        require_admin_access(current_user)
        
        admin_service = AdminAnalyticsService(db)
        
        configurations = {}
        for alert_type, config in admin_service.alert_configs.items():
            configurations[alert_type.value] = {
                "name": config.name,
                "threshold": config.threshold,
                "comparison": config.comparison,
                "enabled": config.enabled,
                "notification_channels": config.notification_channels or []
            }
        
        return {
            "alert_configurations": configurations,
            "total_alerts": len(configurations),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alert configurations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get alert configurations")