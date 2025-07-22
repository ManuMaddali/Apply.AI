"""
Analytics Privacy API Routes

This module provides endpoints for managing user consent, data privacy,
and GDPR compliance for analytics data collection.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import get_db
from services.analytics_privacy_service import AnalyticsPrivacyService, ConsentType
from utils.auth import get_current_user
from models.user import User


# Initialize router and security
router = APIRouter(prefix="/api/analytics/privacy", tags=["analytics-privacy"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class ConsentUpdateRequest(BaseModel):
    consent_updates: Dict[str, bool] = Field(..., description="Consent type -> boolean mapping")
    consent_source: str = Field("user_settings", description="Source of consent update")


class DataDeletionRequest(BaseModel):
    deletion_type: str = Field("all_analytics", description="Type of data to delete")
    confirmation: bool = Field(..., description="User confirmation for deletion")


class DataExportRequest(BaseModel):
    include_anonymized: bool = Field(False, description="Include anonymized data in export")
    format: str = Field("json", description="Export format")


@router.get("/consent")
async def get_user_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's current analytics consent settings
    
    **Returns:**
    - Current consent settings for all analytics types
    - Required vs optional consents based on subscription
    - Consent date and source information
    - Privacy policy compliance status
    
    **Privacy Note:**
    This endpoint helps users understand what data we collect
    and provides transparency about their consent choices.
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        consent_data = await privacy_service.get_user_consent(str(current_user.id))
        
        if "error" in consent_data:
            raise HTTPException(status_code=500, detail=consent_data["error"])
        
        return {
            **consent_data,
            "privacy_policy_url": "/privacy-policy",
            "data_processing_info": {
                "purpose": "Improve user experience and provide analytics insights",
                "legal_basis": "User consent and legitimate interest",
                "data_controller": "ApplyAI Inc.",
                "retention_period": "Based on consent type and subscription tier"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get consent error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve consent settings")


@router.post("/consent")
async def update_user_consent(
    request: ConsentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's analytics consent settings
    
    **Request Body:**
    ```json
    {
        "consent_updates": {
            "basic_analytics": true,
            "performance_tracking": true,
            "usage_analytics": false,
            "improvement_analytics": false,
            "marketing_analytics": false
        },
        "consent_source": "user_settings"
    }
    ```
    
    **Consent Types:**
    - `basic_analytics`: Basic usage patterns (required for Pro)
    - `performance_tracking`: Success rates and optimization (required for Pro)
    - `usage_analytics`: Detailed usage statistics (required for Pro)
    - `improvement_analytics`: Feedback and suggestions (optional)
    - `marketing_analytics`: Marketing effectiveness (optional)
    
    **Note:** Pro users must consent to basic analytics, performance tracking,
    and usage analytics to access Pro features.
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        result = await privacy_service.update_user_consent(
            user_id=str(current_user.id),
            consent_updates=request.consent_updates,
            consent_source=request.consent_source
        )
        
        if "error" in result:
            if "required" in result.get("error", "").lower():
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            **result,
            "message": "Consent settings updated successfully",
            "effective_date": datetime.utcnow().isoformat(),
            "next_steps": "Your new consent preferences will take effect immediately"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update consent error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update consent settings")


@router.get("/data-retention")
async def get_data_retention_policy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data retention policy for the user
    
    **Returns:**
    - Retention periods for different data types
    - Policy version and last update date
    - User-specific retention settings
    
    **Data Retention Periods:**
    - Basic Analytics: 90 days (Free), 365 days (Pro)
    - Performance Tracking: 180 days (Free), 365 days (Pro)
    - Usage Analytics: 365 days (all users)
    - Improvement Analytics: 180 days (all users)
    - Marketing Analytics: 90 days (all users)
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        retention_policy = await privacy_service.get_data_retention_policy(str(current_user.id))
        
        if "error" in retention_policy:
            raise HTTPException(status_code=500, detail=retention_policy["error"])
        
        return {
            **retention_policy,
            "policy_details": {
                "automatic_deletion": "Data is automatically deleted after retention period",
                "user_deletion": "Users can request immediate deletion at any time",
                "backup_retention": "Backups are retained for additional 30 days for recovery",
                "compliance": "Policy complies with GDPR, CCPA, and other privacy regulations"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get retention policy error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve retention policy")


@router.post("/delete-data")
async def request_data_deletion(
    request: DataDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request deletion of analytics data
    
    **Request Body:**
    ```json
    {
        "deletion_type": "all_analytics",
        "confirmation": true
    }
    ```
    
    **Deletion Types:**
    - `all_analytics`: Delete all analytics data
    - `performance_only`: Delete only performance tracking data
    - `usage_only`: Delete only usage analytics data
    
    **Important:**
    - Deletion is irreversible
    - May affect Pro features that depend on analytics
    - Process takes up to 30 days to complete
    - You will receive confirmation when deletion is complete
    """
    try:
        if not request.confirmation:
            raise HTTPException(
                status_code=400, 
                detail="Confirmation required for data deletion request"
            )
        
        privacy_service = AnalyticsPrivacyService(db)
        
        result = await privacy_service.request_data_deletion(
            user_id=str(current_user.id),
            deletion_type=request.deletion_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            **result,
            "important_notes": [
                "Data deletion is irreversible",
                "Some Pro features may be affected",
                "Process takes up to 30 days",
                "You will receive email confirmation when complete"
            ],
            "support_contact": "privacy@applyai.com"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data deletion request error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process data deletion request")


@router.get("/export-data")
async def export_analytics_data(
    include_anonymized: bool = Query(False, description="Include anonymized data"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export user's analytics data for transparency/portability
    
    **Query Parameters:**
    - `include_anonymized`: Include anonymized/aggregated data
    - `format`: Export format (json or csv)
    
    **Returns:**
    Complete export of user's analytics data including:
    - Consent settings and history
    - Usage patterns and statistics
    - Performance metrics
    - Data retention information
    
    **Privacy Note:**
    This export contains all analytics data we have collected
    about you based on your consent settings. Data is provided
    in a portable format for transparency and data portability rights.
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        export_data = await privacy_service.export_user_analytics_data(
            user_id=str(current_user.id),
            include_anonymized=include_anonymized
        )
        
        if "error" in export_data:
            raise HTTPException(status_code=500, detail=export_data["error"])
        
        # Add export metadata
        export_data.update({
            "export_format": format,
            "export_request_date": datetime.utcnow().isoformat(),
            "data_portability_info": {
                "right_to_portability": "GDPR Article 20",
                "format_standard": "Machine-readable JSON/CSV format",
                "usage": "This data can be imported into other analytics systems"
            }
        })
        
        if format == "csv":
            # In a real implementation, would convert to CSV format
            export_data["note"] = "CSV export would be implemented with pandas or similar library"
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data export error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analytics data")


@router.get("/privacy-summary")
async def get_privacy_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive privacy summary for the user
    
    **Returns:**
    - Current consent status
    - Data collection summary
    - Retention policy overview
    - User rights and options
    - Privacy compliance information
    
    **Purpose:**
    Provides users with a complete overview of their privacy
    settings and data handling in one convenient endpoint.
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        # Get all privacy-related information
        consent_data = await privacy_service.get_user_consent(str(current_user.id))
        retention_policy = await privacy_service.get_data_retention_policy(str(current_user.id))
        
        if "error" in consent_data or "error" in retention_policy:
            raise HTTPException(status_code=500, detail="Failed to retrieve privacy information")
        
        return {
            "user_id": str(current_user.id),
            "privacy_summary": {
                "consent_status": consent_data["consent_settings"],
                "data_collection_active": consent_data["can_collect_analytics"],
                "subscription_tier": current_user.subscription_tier,
                "last_consent_update": consent_data.get("consent_date"),
                "retention_periods": retention_policy["retention_policy"]
            },
            "user_rights": {
                "right_to_access": "View all data we have about you",
                "right_to_rectification": "Correct inaccurate data",
                "right_to_erasure": "Request deletion of your data",
                "right_to_portability": "Export your data in machine-readable format",
                "right_to_object": "Object to data processing",
                "right_to_restrict": "Restrict certain data processing"
            },
            "privacy_controls": {
                "update_consent": "POST /api/analytics/privacy/consent",
                "export_data": "GET /api/analytics/privacy/export-data",
                "delete_data": "POST /api/analytics/privacy/delete-data",
                "view_retention": "GET /api/analytics/privacy/data-retention"
            },
            "compliance_info": {
                "regulations": ["GDPR", "CCPA", "PIPEDA"],
                "privacy_policy": "/privacy-policy",
                "contact": "privacy@applyai.com",
                "data_protection_officer": "dpo@applyai.com"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Privacy summary error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate privacy summary")


@router.get("/consent-types")
async def get_consent_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about all consent types
    
    **Returns:**
    Detailed descriptions of each consent type, what data
    is collected, how it's used, and whether it's required
    for the user's subscription tier.
    """
    try:
        privacy_service = AnalyticsPrivacyService(db)
        
        # Get required and optional consents for user's tier
        tier = str(current_user.subscription_tier) if current_user.subscription_tier is not None else "free"
        required_consents = privacy_service._get_required_consents(tier)
        optional_consents = privacy_service._get_optional_consents(tier)
        
        consent_descriptions = {
            ConsentType.BASIC_ANALYTICS: {
                "name": "Basic Analytics",
                "description": "Basic usage patterns and feature adoption metrics",
                "data_collected": ["Feature usage counts", "Session duration", "User flow patterns"],
                "purpose": "Understand how users interact with the application",
                "required": ConsentType.BASIC_ANALYTICS in required_consents
            },
            ConsentType.PERFORMANCE_TRACKING: {
                "name": "Performance Tracking",
                "description": "Success rates, optimization scores, and performance metrics",
                "data_collected": ["Success rates", "Keyword optimization scores", "Template effectiveness"],
                "purpose": "Provide analytics dashboard and performance insights",
                "required": ConsentType.PERFORMANCE_TRACKING in required_consents
            },
            ConsentType.USAGE_ANALYTICS: {
                "name": "Usage Analytics",
                "description": "Detailed usage statistics and behavioral patterns",
                "data_collected": ["Detailed usage logs", "Feature preferences", "Usage trends"],
                "purpose": "Generate personalized recommendations and insights",
                "required": ConsentType.USAGE_ANALYTICS in required_consents
            },
            ConsentType.IMPROVEMENT_ANALYTICS: {
                "name": "Improvement Analytics",
                "description": "Feedback data and improvement suggestions",
                "data_collected": ["User feedback", "Error reports", "Improvement suggestions"],
                "purpose": "Improve product features and user experience",
                "required": ConsentType.IMPROVEMENT_ANALYTICS in required_consents
            },
            ConsentType.MARKETING_ANALYTICS: {
                "name": "Marketing Analytics",
                "description": "Marketing campaign effectiveness and user acquisition data",
                "data_collected": ["Campaign interactions", "Referral sources", "Conversion metrics"],
                "purpose": "Measure marketing effectiveness and optimize campaigns",
                "required": ConsentType.MARKETING_ANALYTICS in required_consents
            }
        }
        
        return {
            "consent_types": {
                consent_type.value: description 
                for consent_type, description in consent_descriptions.items()
            },
            "subscription_tier": current_user.subscription_tier,
            "required_consents": [ct.value for ct in required_consents],
            "optional_consents": [ct.value for ct in optional_consents],
            "note": "Required consents are necessary for your subscription tier's features to work properly"
        }
        
    except Exception as e:
        logger.error(f"Get consent types error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve consent type information")
