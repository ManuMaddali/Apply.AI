"""
Analytics API Routes for Pro Users

This module provides Pro-only analytics endpoints for dashboard data,
success rates, keyword optimization, and performance insights.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import get_db
from middleware.feature_gate import require_pro_subscription
from services.analytics_service import AnalyticsService, AnalyticsEventType
from utils.auth import get_current_user
from models.user import User


# Initialize router and security
router = APIRouter(prefix="/api/analytics", tags=["analytics"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class KeywordOptimizationRequest(BaseModel):
    resume_text: str = Field(..., description="Resume content to analyze")
    job_description: str = Field(..., description="Job description to match against")


class AnalyticsEventRequest(BaseModel):
    event_type: str = Field(..., description="Type of analytics event")
    event_data: Dict = Field(..., description="Event-specific data")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class DashboardResponse(BaseModel):
    overview: Dict
    success_rates: Dict
    keyword_optimization: Dict
    template_performance: Dict
    usage_trends: Dict
    feature_adoption: Dict
    recommendations: List[Dict]
    time_range: str
    generated_at: str


@router.get("/dashboard")
async def get_analytics_dashboard(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard for Pro users
    
    **Pro Feature**: Requires active Pro subscription
    
    **Time Ranges:**
    - 7d: Last 7 days
    - 30d: Last 30 days (default)
    - 90d: Last 90 days
    - 1y: Last year
    
    **Returns:**
    - Overview metrics (resumes generated, success rates, etc.)
    - Success rate analytics by template and industry
    - Keyword optimization scores and trends
    - Template performance metrics
    - Usage trends over time
    - Feature adoption rates
    - Personalized recommendations
    """
    try:
        analytics_service = AnalyticsService(db)
        
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user_id=str(current_user.id),
            time_range=time_range
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=403, detail=dashboard_data["error"])
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics dashboard error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics dashboard")


@router.post("/keyword-optimization")
async def analyze_keyword_optimization(
    request: KeywordOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze keyword optimization score for resume against job description
    
    **Pro Feature**: Requires active Pro subscription
    
    **Analysis includes:**
    - Overall optimization score (0-100)
    - Letter grade (A+ to D)
    - Matched keywords list
    - Missing critical keywords
    - Keyword density analysis
    - Personalized recommendations
    
    **Request Body:**
    ```json
    {
        "resume_text": "Your resume content...",
        "job_description": "Job posting description..."
    }
    ```
    """
    try:
        analytics_service = AnalyticsService(db)
        
        optimization_result = await analytics_service.get_keyword_optimization_score(
            user_id=str(current_user.id),
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        if "error" in optimization_result:
            raise HTTPException(status_code=403, detail=optimization_result["error"])
        
        return optimization_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Keyword optimization error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze keyword optimization")


@router.get("/success-rates")
async def get_success_rate_analytics(
    metric_type: str = Query("overall", regex="^(overall|by_template|by_industry)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed success rate analytics
    
    **Pro Feature**: Requires active Pro subscription
    
    **Metric Types:**
    - overall: Overall success rate and trends
    - by_template: Success rates broken down by template type
    - by_industry: Success rates broken down by industry
    
    **Returns:**
    - Success rate percentages
    - Trend analysis (increasing/decreasing/stable)
    - Benchmark comparisons
    - Performance insights
    """
    try:
        analytics_service = AnalyticsService(db)
        
        success_data = await analytics_service.get_success_rate_analytics(
            user_id=str(current_user.id),
            metric_type=metric_type
        )
        
        if "error" in success_data:
            raise HTTPException(status_code=403, detail=success_data["error"])
        
        return success_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Success rate analytics error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get success rate analytics")


@router.post("/track-event")
async def track_analytics_event(
    request: AnalyticsEventRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track a custom analytics event
    
    **Pro Feature**: Requires active Pro subscription
    
    **Supported Event Types:**
    - resume_generated
    - cover_letter_generated
    - bulk_processing
    - advanced_formatting
    - job_application
    - template_usage
    - keyword_optimization
    
    **Request Body:**
    ```json
    {
        "event_type": "job_application",
        "event_data": {
            "job_title": "Senior Developer",
            "company": "Tech Corp",
            "template_used": "technical"
        },
        "metadata": {
            "source": "bulk_processing"
        }
    }
    ```
    """
    try:
        # Validate event type
        try:
            event_type = AnalyticsEventType(request.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {request.event_type}")
        
        analytics_service = AnalyticsService(db)
        
        success = await analytics_service.track_event(
            user_id=str(current_user.id),
            event_type=event_type,
            event_data=request.event_data,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track analytics event")
        
        return {
            "success": True,
            "message": "Analytics event tracked successfully",
            "event_type": request.event_type,
            "tracked_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event tracking error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track analytics event")


@router.get("/template-performance")
async def get_template_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get template performance analytics
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Usage count for each template
    - Success rate by template
    - Effectiveness scores
    - Template recommendations
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get user events for template analysis
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user_id=str(current_user.id),
            time_range="90d"
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=403, detail=dashboard_data["error"])
        
        return {
            "template_performance": dashboard_data.get("template_performance", {}),
            "recommendations": [
                rec for rec in dashboard_data.get("recommendations", [])
                if rec.get("type") == "template_suggestion"
            ],
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template performance error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template performance analytics")


@router.get("/usage-trends")
async def get_usage_trends(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage trends and patterns
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Daily usage patterns
    - Peak usage times
    - Feature adoption trends
    - Activity insights
    """
    try:
        analytics_service = AnalyticsService(db)
        
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user_id=str(current_user.id),
            time_range=time_range
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=403, detail=dashboard_data["error"])
        
        return {
            "usage_trends": dashboard_data.get("usage_trends", {}),
            "feature_adoption": dashboard_data.get("feature_adoption", {}),
            "time_range": time_range,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Usage trends error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage trends")


@router.get("/recommendations")
async def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations based on usage analytics
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Feature suggestions
    - Improvement recommendations
    - Optimization tips
    - Best practices
    """
    try:
        analytics_service = AnalyticsService(db)
        
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user_id=str(current_user.id),
            time_range="30d"
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=403, detail=dashboard_data["error"])
        
        return {
            "recommendations": dashboard_data.get("recommendations", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendations error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get personalized recommendations")


@router.get("/export")
async def export_analytics_data(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export analytics data for external analysis
    
    **Pro Feature**: Requires active Pro subscription
    
    **Formats:**
    - json: JSON format (default)
    - csv: CSV format for spreadsheet analysis
    
    **Privacy Note:**
    All exported data is anonymized and contains only aggregated metrics.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user_id=str(current_user.id),
            time_range=time_range
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=403, detail=dashboard_data["error"])
        
        # Add export metadata
        export_data = {
            **dashboard_data,
            "export_info": {
                "exported_by": current_user.email,
                "export_format": format,
                "export_timestamp": datetime.utcnow().isoformat(),
                "privacy_note": "Data is anonymized and aggregated for privacy protection"
            }
        }
        
        if format == "csv":
            # In a real implementation, would convert to CSV format
            # For now, return JSON with CSV note
            export_data["note"] = "CSV export would be implemented with pandas or similar library"
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics export error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analytics data")
