"""
Premium Cover Letter API Routes for Pro Users

This module provides Pro-only cover letter endpoints with advanced templates,
custom tones, and enhanced AI generation capabilities.
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
from services.premium_cover_letter_service import (
    PremiumCoverLetterService,
    CoverLetterTemplate,
    CoverLetterTone
)
from utils.auth import get_current_user
from models.user import User


# Initialize router and security
router = APIRouter(prefix="/api/premium/cover-letters", tags=["premium-cover-letters"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class PremiumCoverLetterRequest(BaseModel):
    resume_text: str = Field(..., description="User's resume content")
    job_description: str = Field(..., description="Job posting description")
    company_name: str = Field(..., description="Target company name")
    job_title: str = Field(..., description="Target job title")
    template: str = Field("professional", description="Cover letter template")
    tone: str = Field("professional", description="Cover letter tone")
    custom_instructions: Optional[str] = Field(None, description="Additional user instructions")
    include_metrics: bool = Field(True, description="Emphasize quantifiable achievements")
    include_company_research: bool = Field(True, description="Include company-specific insights")


class CoverLetterResponse(BaseModel):
    cover_letter: str
    template_used: str
    tone_used: str
    premium_features: Dict
    generated_at: str
    word_count: int
    character_count: int


class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    focus: str
    tone: str
    premium: bool


class ToneInfo(BaseModel):
    id: str
    name: str
    description: str


@router.post("/generate", response_model=CoverLetterResponse)
async def generate_premium_cover_letter(
    request: PremiumCoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a premium cover letter with advanced AI and templates
    
    **Pro Feature**: Requires active Pro subscription
    
    **Premium Features:**
    - Advanced AI prompts with GPT-4
    - Industry-specific templates
    - Custom tone options
    - Company research integration
    - Metrics emphasis
    - Custom instructions support
    
    **Available Templates:**
    - executive: For C-suite and leadership positions
    - creative: For design and creative roles
    - technical: For engineering positions
    - consulting: For consulting and strategy roles
    - startup: For startup and entrepreneurial roles
    - academic: For research and academic positions
    - sales: For sales and business development
    - healthcare: For medical and healthcare positions
    
    **Available Tones:**
    - professional: Formal and business-focused
    - conversational: Friendly and approachable
    - confident: Assertive and self-assured
    - enthusiastic: Energetic and passionate
    - analytical: Data-driven and logical
    - creative: Innovative and expressive
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        # Validate template
        try:
            template_enum = CoverLetterTemplate(request.template)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid template: {request.template}. Available templates: {[t.value for t in CoverLetterTemplate]}"
            )
        
        # Validate tone
        try:
            tone_enum = CoverLetterTone(request.tone)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tone: {request.tone}. Available tones: {[t.value for t in CoverLetterTone]}"
            )
        
        # Initialize service
        cover_letter_service = PremiumCoverLetterService(db)
        
        # Generate premium cover letter
        result = await cover_letter_service.generate_premium_cover_letter(
            user_id=str(current_user.id),
            resume_text=request.resume_text,
            job_description=request.job_description,
            company_name=request.company_name,
            job_title=request.job_title,
            template=template_enum,
            tone=tone_enum,
            custom_instructions=request.custom_instructions,
            include_metrics=request.include_metrics,
            include_company_research=request.include_company_research
        )
        
        return CoverLetterResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Premium cover letter generation error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate premium cover letter")


@router.get("/templates", response_model=List[TemplateInfo])
async def get_available_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available cover letter templates based on subscription
    
    **Free Users**: Get basic template only
    **Pro Users**: Get all premium templates
    
    **Returns:**
    List of available templates with descriptions and focus areas
    """
    try:
        cover_letter_service = PremiumCoverLetterService(db)
        
        templates = cover_letter_service.get_available_templates(str(current_user.id))
        
        return [TemplateInfo(**template) for template in templates]
        
    except Exception as e:
        logger.error(f"Get templates error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available templates")


@router.get("/tones", response_model=List[ToneInfo])
async def get_available_tones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available cover letter tones
    
    **Pro Feature**: Requires active Pro subscription
    
    **Available Tones:**
    - Professional: Formal and business-focused
    - Conversational: Friendly and approachable
    - Confident: Assertive and self-assured
    - Enthusiastic: Energetic and passionate
    - Analytical: Data-driven and logical
    - Creative: Innovative and expressive
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        cover_letter_service = PremiumCoverLetterService(db)
        
        tones = cover_letter_service.get_available_tones()
        
        return [ToneInfo(**tone) for tone in tones]
        
    except Exception as e:
        logger.error(f"Get tones error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available tones")


@router.get("/template/{template_id}")
async def get_template_details(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific template
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Template configuration
    - Focus areas
    - Best use cases
    - Sample output characteristics
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        # Validate template ID
        try:
            template_enum = CoverLetterTemplate(template_id)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        
        cover_letter_service = PremiumCoverLetterService(db)
        
        # Get template configuration
        template_config = cover_letter_service.premium_templates.get(template_enum)
        
        if not template_config:
            raise HTTPException(status_code=404, detail=f"Template configuration not found: {template_id}")
        
        return {
            "id": template_id,
            "name": template_config["name"],
            "description": template_config["description"],
            "focus": template_config["focus"],
            "tone": template_config["tone"],
            "best_for": f"Ideal for {template_config['description'].lower()}",
            "characteristics": {
                "style": template_config["tone"],
                "focus_areas": template_config["focus"].split(", "),
                "premium": True
            },
            "sample_opening": f"This template creates {template_config['tone']} cover letters that emphasize {template_config['focus']}."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template details error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template details")


class PreviewRequest(BaseModel):
    template: str = Field(..., description="Template to preview")
    tone: str = Field(..., description="Tone to preview")

@router.post("/preview")
async def preview_cover_letter_style(
    request: PreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview cover letter style without generating full content
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Sample opening paragraph
    - Style characteristics
    - Expected tone and focus
    - Template recommendations
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        # Validate template and tone
        try:
            template_enum = CoverLetterTemplate(request.template)
            tone_enum = CoverLetterTone(request.tone)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid template or tone: {str(e)}")
        
        cover_letter_service = PremiumCoverLetterService(db)
        
        # Get template and tone configurations
        template_config = cover_letter_service.premium_templates[template_enum]
        tone_description = cover_letter_service._get_tone_description(tone_enum)
        
        # Generate preview content
        preview_content = f"""
**Template Style Preview: {template_config['name']}**

**Focus Areas:** {template_config['focus']}
**Tone:** {tone_enum.value.title()} - {tone_description}

**Sample Opening Style:**
"Dear Hiring Manager,

I am writing to express my strong interest in the [Position] role at [Company]. With my background in {template_config['focus'].split(',')[0].strip()}, I am excited about the opportunity to contribute to your team's success..."

**This template will:**
- Emphasize {template_config['focus']}
- Maintain a {tone_enum.value} tone throughout
- {template_config['tone']} approach to positioning your experience
- Include industry-specific terminology and insights
"""
        
        return {
            "template": template,
            "tone": tone,
            "preview_content": preview_content.strip(),
            "characteristics": {
                "focus_areas": template_config['focus'].split(', '),
                "tone_style": tone_description,
                "template_approach": template_config['tone']
            },
            "recommendations": [
                f"Best for: {template_config['description']}",
                f"Tone style: {tone_description}",
                f"Emphasizes: {template_config['focus']}"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cover letter preview error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter preview")


@router.get("/usage-stats")
async def get_cover_letter_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cover letter usage statistics for the user
    
    **Pro Feature**: Requires active Pro subscription
    
    **Returns:**
    - Total cover letters generated
    - Template usage breakdown
    - Tone preferences
    - Success metrics
    - Usage trends
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        # This would integrate with the analytics service
        # For now, return mock data
        
        return {
            "total_generated": 23,
            "this_month": 8,
            "template_usage": {
                "technical": 12,
                "professional": 6,
                "creative": 3,
                "executive": 2
            },
            "tone_preferences": {
                "professional": 15,
                "confident": 5,
                "conversational": 3
            },
            "success_metrics": {
                "average_word_count": 287,
                "average_generation_time": "3.2s",
                "user_satisfaction": "4.8/5"
            },
            "recent_activity": [
                {
                    "date": "2024-01-15",
                    "template": "technical",
                    "tone": "professional",
                    "company": "Tech Corp"
                },
                {
                    "date": "2024-01-14",
                    "template": "executive",
                    "tone": "confident",
                    "company": "Leadership Inc"
                }
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cover letter usage stats error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")


class FeedbackRequest(BaseModel):
    cover_letter_id: str = Field(..., description="ID of the generated cover letter")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback: Optional[str] = Field(None, description="Optional feedback text")

@router.post("/feedback")
async def submit_cover_letter_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a generated cover letter
    
    **Pro Feature**: Requires active Pro subscription
    
    **Purpose:**
    - Improve AI generation quality
    - Personalize future recommendations
    - Track user satisfaction
    - Enhance template effectiveness
    """
    try:
        # Check Pro subscription requirement
        await require_pro_subscription(current_user)
        
        # Store feedback (would integrate with analytics service)
        feedback_data = {
            "user_id": str(current_user.id),
            "cover_letter_id": request.cover_letter_id,
            "rating": request.rating,
            "feedback": request.feedback,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        # Log feedback for analytics
        logger.info(f"Cover letter feedback: {feedback_data}")
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": f"fb_{datetime.utcnow().timestamp()}",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cover letter feedback error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
