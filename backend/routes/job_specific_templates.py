"""
Job-Specific Templates API Routes

This module provides API endpoints for job-specific premium templates:
- Get available job categories
- Get templates for specific categories
- Suggest job categories based on job titles
- Validate job-specific template requests
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from models.user import User
from utils.auth import AuthManager
from services.job_specific_templates import JobSpecificTemplateService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize job-specific template service
job_template_service = JobSpecificTemplateService()


class JobCategorySuggestionRequest(BaseModel):
    job_title: str
    job_description: Optional[str] = None


class TemplateValidationRequest(BaseModel):
    job_category: str
    formatting_template: str


@router.get("/categories")
async def get_job_categories(user: User = Depends(AuthManager.verify_token)):
    """
    Get available job categories for job-specific templates
    
    Returns different responses based on user subscription:
    - Free users: Preview information with upgrade prompts
    - Pro users: Full list of available categories with details
    """
    try:
        categories = job_template_service.get_available_job_categories(user.is_pro_active())
        
        return JSONResponse(content={
            "success": True,
            "categories": categories,
            "user_tier": "pro" if user.is_pro_active() else "free",
            "total_categories": len(categories),
            "pro_required": not user.is_pro_active()
        })
        
    except Exception as e:
        logger.error(f"Error getting job categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job categories: {str(e)}")


@router.get("/categories/{category}")
async def get_job_category_details(category: str, user: User = Depends(AuthManager.verify_token)):
    """
    Get detailed information about a specific job category including:
    - Available template variations
    - Recommended formatting options
    - Industry-specific sections
    - ATS keywords and optimization tips
    """
    try:
        category_details = job_template_service.get_job_category_templates(category, user.is_pro_active())
        
        # Handle error responses from the service
        if isinstance(category_details, dict) and "error" in category_details:
            if "Pro subscription required" in category_details.get("message", ""):
                raise HTTPException(status_code=402, detail=category_details["message"])
            elif "not found" in category_details.get("message", ""):
                raise HTTPException(status_code=404, detail=category_details["message"])
            else:
                raise HTTPException(status_code=400, detail=category_details["message"])
        
        return JSONResponse(content={
            "success": True,
            "category_details": category_details,
            "user_tier": "pro" if user.is_pro_active() else "free"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job category details for {category}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get category details: {str(e)}")


@router.post("/suggest-category")
async def suggest_job_category(request: JobCategorySuggestionRequest, user: User = Depends(AuthManager.verify_token)):
    """
    Suggest the most appropriate job category based on job title and optional job description
    
    This endpoint helps users find the best job-specific template by analyzing:
    - Job title keywords
    - Job description content (if provided)
    - Industry patterns and common role classifications
    """
    try:
        if not request.job_title.strip():
            raise HTTPException(status_code=400, detail="job_title cannot be empty")
        
        # Get suggestion based on job title
        suggested_category = job_template_service.get_job_category_by_title(request.job_title)
        
        response_data = {
            "success": True,
            "job_title": request.job_title,
            "suggested_category": suggested_category.value if suggested_category else None,
            "user_tier": "pro" if user.is_pro_active() else "free",
            "confidence": "high" if suggested_category else "none"
        }
        
        # If a category is suggested and user is Pro, include detailed template info
        if suggested_category and user.is_pro_active():
            try:
                category_details = job_template_service.get_job_category_templates(
                    suggested_category.value, user.is_pro_active()
                )
                response_data["category_details"] = category_details
                response_data["templates_available"] = len(category_details.get("templates", []))
            except Exception as e:
                logger.warning(f"Could not get category details for suggested category {suggested_category.value}: {e}")
        
        # If no suggestion found, provide alternatives
        if not suggested_category:
            response_data["message"] = "No specific job category match found. Consider using general templates or contact support for custom categories."
            response_data["alternatives"] = [
                "software_engineer",  # Most common fallback
                "business_analyst",
                "project_manager"
            ]
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting job category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest job category: {str(e)}")


@router.post("/validate")
async def validate_template_request(request: TemplateValidationRequest, user: User = Depends(AuthManager.verify_token)):
    """
    Validate a job-specific template request before processing
    
    This endpoint checks:
    - User subscription status (Pro required)
    - Job category availability
    - Template format validity
    - Compatibility between category and template
    """
    try:
        is_valid, validation_message = job_template_service.validate_job_specific_request(
            request.job_category,
            request.formatting_template,
            user.is_pro_active()
        )
        
        response_data = {
            "success": True,
            "valid": is_valid,
            "message": validation_message,
            "job_category": request.job_category,
            "formatting_template": request.formatting_template,
            "user_tier": "pro" if user.is_pro_active() else "free"
        }
        
        # If validation failed due to subscription, provide upgrade info
        if not is_valid and "Pro subscription" in validation_message:
            response_data["upgrade_required"] = True
            response_data["upgrade_url"] = "/upgrade"
        
        # If validation failed due to invalid category, provide alternatives
        if not is_valid and "Invalid job category" in validation_message:
            available_categories = [cat.value for cat in job_template_service.job_configs.keys()]
            response_data["available_categories"] = available_categories[:10]  # Limit to first 10
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error validating template request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate template request: {str(e)}")


@router.get("/preview/{category}/{template}")
async def get_template_preview(category: str, template: str, user: User = Depends(AuthManager.verify_token)):
    """
    Get preview information for a specific job category and template combination
    
    Returns:
    - Template preview URL (if available)
    - Template description and features
    - Recommended use cases
    - Sample sections and formatting
    """
    try:
        # Validate user access
        if not user.is_pro_active():
            raise HTTPException(
                status_code=402, 
                detail="Template previews require Pro subscription"
            )
        
        # Validate template request
        is_valid, validation_message = job_template_service.validate_job_specific_request(
            category, template, user.is_pro_active()
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # Get category details
        category_details = job_template_service.get_job_category_templates(category, True)
        
        # Find the specific template
        template_info = None
        for tmpl in category_details.get("templates", []):
            if tmpl["template"] == template:
                template_info = tmpl
                break
        
        if not template_info:
            raise HTTPException(status_code=404, detail=f"Template '{template}' not found for category '{category}'")
        
        preview_data = {
            "success": True,
            "category": category,
            "template": template,
            "template_info": template_info,
            "category_details": {
                "display_name": category_details.get("display_name"),
                "description": category_details.get("description"),
                "industry": category_details.get("industry"),
                "specific_sections": category_details.get("specific_sections", []),
                "recommended_colors": category_details.get("recommended_colors", []),
                "ats_keywords": category_details.get("ats_keywords", [])
            },
            "preview_available": True,
            "sample_sections": [
                "Professional Summary",
                "Technical Skills" if "technical" in category.lower() else "Core Competencies",
                "Professional Experience",
                "Education",
                "Certifications"
            ]
        }
        
        return JSONResponse(content=preview_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template preview for {category}/{template}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get template preview: {str(e)}")


@router.get("/stats")
async def get_template_usage_stats(user: User = Depends(AuthManager.verify_token)):
    """
    Get usage statistics for job-specific templates (Pro users only)
    
    Returns:
    - Most popular job categories
    - Template usage patterns
    - User's template history (if available)
    """
    try:
        if not user.is_pro_active():
            raise HTTPException(
                status_code=402,
                detail="Template statistics require Pro subscription"
            )
        
        # This would typically come from a database in a real implementation
        # For now, return mock statistics
        stats_data = {
            "success": True,
            "user_tier": "pro",
            "popular_categories": [
                {"category": "software_engineer", "usage_count": 1250, "percentage": 28.5},
                {"category": "data_scientist", "usage_count": 890, "percentage": 20.3},
                {"category": "product_manager", "usage_count": 675, "percentage": 15.4},
                {"category": "financial_manager", "usage_count": 445, "percentage": 10.1},
                {"category": "sales_representative", "usage_count": 380, "percentage": 8.7}
            ],
            "popular_templates": [
                {"template": "modern", "usage_count": 1680, "percentage": 38.2},
                {"template": "technical", "usage_count": 1120, "percentage": 25.5},
                {"template": "executive", "usage_count": 890, "percentage": 20.3},
                {"template": "standard", "usage_count": 710, "percentage": 16.0}
            ],
            "total_categories": len(job_template_service.job_configs),
            "total_templates_available": len(job_template_service.job_configs) * 7,  # 7 templates per category
            "user_usage": {
                "templates_used": 0,  # Would come from user's history
                "favorite_category": None,
                "last_used": None
            }
        }
        
        return JSONResponse(content=stats_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get template statistics: {str(e)}")