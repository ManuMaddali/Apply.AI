"""
Analytics Dashboard API Routes
Phase 3: Advanced analytics endpoints for performance tracking and insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from services.analytics_dashboard_service import AnalyticsDashboardService
from utils.auth import AuthManager

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

# Initialize services
analytics_service = AnalyticsDashboardService()
auth_manager = AuthManager()

@router.get("/dashboard")
async def get_analytics_dashboard(
    time_period: str = Query("30d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get comprehensive analytics dashboard overview
    
    Args:
        time_period: Analysis period (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        Comprehensive analytics dashboard data
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching analytics dashboard for user {user_id}, period: {time_period}")
        
        dashboard_data = await analytics_service.get_dashboard_overview(user_id, time_period)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": dashboard_data,
                "message": f"Analytics dashboard retrieved for {time_period} period"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching analytics dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics dashboard: {str(e)}")

@router.get("/success-rates")
async def get_success_rate_analysis(
    time_period: str = Query("30d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get detailed success rate analysis
    
    Args:
        time_period: Analysis period (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        Detailed success rate metrics and analysis
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching success rate analysis for user {user_id}, period: {time_period}")
        
        success_data = await analytics_service.get_success_rate_analysis(user_id, time_period)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": success_data,
                "message": "Success rate analysis retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching success rate analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch success rate analysis: {str(e)}")

@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", regex="^(json|csv)$"),
    time_period: str = Query("90d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Export analytics data for user
    
    Args:
        format: Export format (json, csv)
        time_period: Data period to export (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        Exported analytics data
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Exporting analytics data for user {user_id}, format: {format}, period: {time_period}")
        
        export_data = await analytics_service.export_analytics_data(user_id, format)
        
        if format == "csv":
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": export_data,
                    "message": "Analytics data exported as CSV"
                },
                headers={"Content-Type": "application/json"}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": export_data,
                    "message": "Analytics data exported as JSON"
                }
            )
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export analytics data: {str(e)}")

@router.get("/insights")
async def get_personalized_insights(
    category: Optional[str] = Query(None, regex="^(template|keyword|timing|optimization)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get personalized insights and recommendations
    
    Args:
        category: Filter insights by category (optional)
        user: Authenticated user object
    
    Returns:
        Personalized insights and recommendations
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching personalized insights for user {user_id}, category: {category}")
        
        dashboard_data = await analytics_service.get_dashboard_overview(user_id, "30d")
        insights = dashboard_data.get("success_insights", [])
        recommendations = dashboard_data.get("recommendations", [])
        
        # Filter by category if specified
        if category:
            insights = [insight for insight in insights if category.lower() in insight.get("category", "").lower()]
            recommendations = [rec for rec in recommendations if category.lower() in rec.get("category", "").lower()]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "insights": insights,
                    "recommendations": recommendations,
                    "category_filter": category
                },
                "message": f"Personalized insights retrieved{f' for {category}' if category else ''}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching personalized insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch personalized insights: {str(e)}")

@router.get("/metrics/ats-trends")
async def get_ats_score_trends(
    time_period: str = Query("30d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get ATS score trends over time
    
    Args:
        time_period: Analysis period (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        ATS score trends and component analysis
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching ATS trends for user {user_id}, period: {time_period}")
        
        dashboard_data = await analytics_service.get_dashboard_overview(user_id, time_period)
        ats_trends = dashboard_data.get("detailed_metrics", {}).get("ats_trends", {})
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": ats_trends,
                "message": "ATS score trends retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching ATS trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ATS trends: {str(e)}")

@router.get("/metrics/template-performance")
async def get_template_performance(
    time_period: str = Query("30d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get template performance analysis
    
    Args:
        time_period: Analysis period (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        Template performance metrics and recommendations
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching template performance for user {user_id}, period: {time_period}")
        
        dashboard_data = await analytics_service.get_dashboard_overview(user_id, time_period)
        template_performance = dashboard_data.get("detailed_metrics", {}).get("template_performance", {})
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": template_performance,
                "message": "Template performance analysis retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching template performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch template performance: {str(e)}")

@router.get("/metrics/keyword-optimization")
async def get_keyword_optimization_insights(
    time_period: str = Query("30d", regex="^(7d|30d|90d)$"),
    user = Depends(auth_manager.verify_token)
):
    """
    Get keyword optimization insights and recommendations
    
    Args:
        time_period: Analysis period (7d, 30d, 90d)
        user: Authenticated user object
    
    Returns:
        Keyword optimization analysis and suggestions
    """
    try:
        user_id = str(user.id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        logger.info(f"Fetching keyword insights for user {user_id}, period: {time_period}")
        
        dashboard_data = await analytics_service.get_dashboard_overview(user_id, time_period)
        keyword_insights = dashboard_data.get("detailed_metrics", {}).get("keyword_insights", {})
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": keyword_insights,
                "message": "Keyword optimization insights retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching keyword insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch keyword insights: {str(e)}")

@router.get("/health")
async def analytics_health_check():
    """Health check endpoint for analytics service"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "service": "analytics_dashboard",
            "status": "healthy",
            "version": "3.0.0",
            "features": [
                "dashboard_overview",
                "success_rate_analysis", 
                "ats_trends",
                "template_performance",
                "keyword_optimization",
                "personalized_insights",
                "data_export"
            ]
        }
    )
