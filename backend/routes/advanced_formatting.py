"""
Advanced Formatting API Routes - Pro-only PDF formatting endpoints

This module provides:
- Advanced formatting options for Pro users
- Template and color scheme selection
- Custom formatting parameters
- ATS compatibility validation
- Fallback to standard formatting for Free users
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import tempfile
import os
import logging

from config.database import get_db
from utils.auth import get_current_user
from models.user import User
from services.advanced_formatting_service import (
    AdvancedFormattingService,
    FormattingOptions,
    FormattingTemplate,
    ColorScheme,
    FontFamily
)
from middleware.feature_gate import require_pro_subscription

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resumes/advanced-format", tags=["Advanced Formatting"])


class AdvancedFormatRequest(BaseModel):
    """Request model for advanced formatting"""
    resume_text: str = Field(..., description="Resume text content to format")
    job_title: Optional[str] = Field(None, description="Job title for context")
    template: str = Field(FormattingTemplate.STANDARD.value, description="Formatting template")
    color_scheme: str = Field(ColorScheme.CLASSIC_BLUE.value, description="Color scheme")
    font_family: str = Field(FontFamily.HELVETICA.value, description="Font family")
    font_size: int = Field(10, ge=8, le=14, description="Font size (8-14)")
    line_spacing: float = Field(1.2, ge=1.0, le=2.0, description="Line spacing (1.0-2.0)")
    margin_size: float = Field(0.5, ge=0.3, le=1.0, description="Margin size in inches")
    section_spacing: float = Field(12, ge=6, le=24, description="Section spacing in points")
    use_two_columns: bool = Field(False, description="Use two-column layout")
    include_border: bool = Field(False, description="Include decorative borders")
    header_style: str = Field("underline", description="Section header style")
    bullet_style: str = Field("circle", description="Bullet point style")
    page_size: str = Field("letter", description="Page size (letter/a4)")
    filename: Optional[str] = Field(None, description="Custom filename")


class TemplateListResponse(BaseModel):
    """Response model for template list"""
    templates: List[Dict[str, Any]]
    color_schemes: List[Dict[str, Any]]
    font_families: List[str]


class FormattingValidationResponse(BaseModel):
    """Response model for formatting validation"""
    valid: bool
    message: str
    ats_compatible: bool
    warnings: List[str] = []


@router.get("/templates", response_model=TemplateListResponse)
async def get_available_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available formatting templates and options"""
    try:
        formatting_service = AdvancedFormattingService()
        
        # Check if user is Pro
        is_pro = current_user.is_pro_active()
        
        # Get available templates
        templates = formatting_service.get_available_templates(is_pro)
        color_schemes = formatting_service.get_available_color_schemes()
        font_families = [font.value for font in FontFamily]
        
        return TemplateListResponse(
            templates=templates,
            color_schemes=color_schemes,
            font_families=font_families
        )
        
    except Exception as e:
        logger.error(f"Error getting available templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve formatting options"
        )


@router.post("/validate", response_model=FormattingValidationResponse)
async def validate_formatting_options(
    request: AdvancedFormatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate formatting options and check ATS compatibility"""
    try:
        formatting_service = AdvancedFormattingService()
        
        # Check if user can use the requested template
        is_pro = current_user.is_pro_active()
        is_valid, message = formatting_service.validate_formatting_request(
            request.template,
            request.color_scheme,
            request.font_family,
            is_pro
        )
        
        if not is_valid:
            return FormattingValidationResponse(
                valid=False,
                message=message,
                ats_compatible=False,
                warnings=[message]
            )
        
        # Create formatting options
        formatting_options = FormattingOptions(
            template=FormattingTemplate(request.template),
            color_scheme=ColorScheme(request.color_scheme),
            font_family=FontFamily(request.font_family),
            font_size=request.font_size,
            line_spacing=request.line_spacing,
            margin_size=request.margin_size,
            section_spacing=request.section_spacing,
            use_two_columns=request.use_two_columns,
            include_border=request.include_border,
            header_style=request.header_style,
            bullet_style=request.bullet_style,
            page_size=request.page_size
        )
        
        # Check ATS compatibility
        ats_compatible = formatting_service._validate_ats_compatibility(formatting_options)
        warnings = []
        
        if not ats_compatible:
            warnings.append("Some formatting options may not be ATS compatible")
            if request.use_two_columns:
                warnings.append("Two-column layouts may not parse correctly in ATS systems")
            if request.font_size < 9 or request.font_size > 12:
                warnings.append("Font size outside 9-12 range may not be ATS friendly")
            if request.template == FormattingTemplate.CREATIVE.value:
                warnings.append("Creative templates may not be optimal for ATS parsing")
        
        return FormattingValidationResponse(
            valid=True,
            message="Formatting options are valid",
            ats_compatible=ats_compatible,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Error validating formatting options: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate formatting options"
        )


@router.post("/generate")
async def generate_advanced_formatted_resume(
    request: AdvancedFormatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an advanced formatted resume PDF (Pro users only)"""
    try:
        formatting_service = AdvancedFormattingService()
        
        # Check if user can use advanced formatting
        is_pro = current_user.is_pro_active()
        
        # Validate formatting request
        is_valid, validation_message = formatting_service.validate_formatting_request(
            request.template,
            request.color_scheme,
            request.font_family,
            is_pro
        )
        
        if not is_valid:
            # For non-Pro users requesting Pro features, return upgrade message
            if "requires Pro subscription" in validation_message:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "subscription_required",
                        "message": "Advanced formatting requires Pro subscription",
                        "upgrade_url": "/upgrade",
                        "feature": "advanced_formatting"
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation_message
                )
        
        # Create formatting options
        formatting_options = FormattingOptions(
            template=FormattingTemplate(request.template),
            color_scheme=ColorScheme(request.color_scheme),
            font_family=FontFamily(request.font_family),
            font_size=request.font_size,
            line_spacing=request.line_spacing,
            margin_size=request.margin_size,
            section_spacing=request.section_spacing,
            use_two_columns=request.use_two_columns,
            include_border=request.include_border,
            header_style=request.header_style,
            bullet_style=request.bullet_style,
            page_size=request.page_size
        )
        
        # Create temporary file for PDF
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        
        try:
            # Generate the formatted resume
            if is_pro and request.template != FormattingTemplate.STANDARD.value:
                # Use advanced formatting for Pro users
                success = formatting_service.create_advanced_formatted_resume(
                    request.resume_text,
                    formatting_options,
                    temp_path,
                    request.job_title or ""
                )
            else:
                # Use standard formatting (fallback)
                success = formatting_service.create_standard_formatted_resume(
                    request.resume_text,
                    temp_path,
                    request.job_title or ""
                )
            
            if not success:
                # Try fallback to standard formatting
                logger.warning("Advanced formatting failed, falling back to standard")
                success = formatting_service.create_standard_formatted_resume(
                    request.resume_text,
                    temp_path,
                    request.job_title or ""
                )
                
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to generate formatted resume"
                    )
            
            # Read the generated PDF
            with open(temp_path, 'rb') as f:
                pdf_content = f.read()
            
            # Determine filename
            filename = request.filename or f"resume_{request.template}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Return PDF response
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "X-Template-Used": request.template,
                    "X-ATS-Compatible": str(formatting_service._validate_ats_compatibility(formatting_options))
                }
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating advanced formatted resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate formatted resume"
        )


@router.post("/generate-standard")
async def generate_standard_formatted_resume(
    request: AdvancedFormatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a standard formatted resume PDF (available to all users)"""
    try:
        formatting_service = AdvancedFormattingService()
        
        # Create temporary file for PDF
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        
        try:
            # Generate standard formatted resume
            success = formatting_service.create_standard_formatted_resume(
                request.resume_text,
                temp_path,
                request.job_title or ""
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate standard formatted resume"
                )
            
            # Read the generated PDF
            with open(temp_path, 'rb') as f:
                pdf_content = f.read()
            
            # Determine filename
            filename = request.filename or f"resume_standard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Return PDF response
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "X-Template-Used": "standard",
                    "X-ATS-Compatible": "true"
                }
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating standard formatted resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate standard formatted resume"
        )


@router.get("/preview/{template}")
async def get_template_preview(
    template: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a preview image for a specific template"""
    try:
        formatting_service = AdvancedFormattingService()
        
        # Validate template
        try:
            template_enum = FormattingTemplate(template)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template: {template}"
            )
        
        # Check if user can access this template
        is_pro = current_user.is_pro_active()
        if template_enum != FormattingTemplate.STANDARD and not is_pro:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "subscription_required",
                    "message": f"Template '{template}' requires Pro subscription",
                    "upgrade_url": "/upgrade"
                }
            )
        
        # For now, return a placeholder response
        # In a full implementation, you would serve actual preview images
        preview_path = f"/static/templates/{template}_preview.png"
        
        return {
            "template": template,
            "preview_url": preview_path,
            "available": True,
            "pro_only": template_enum != FormattingTemplate.STANDARD
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template preview"
        )