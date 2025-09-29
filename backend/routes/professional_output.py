"""
Professional Output API Routes - Phase 2 Advanced Features
Provides ATS-optimized PDF/Word generation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

# Import services
try:
    from services.professional_output_service import ProfessionalOutputService
    from utils.auth import get_current_user
    from config.database import get_db
    SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Professional output service not available: {e}")
    SERVICE_AVAILABLE = False
    
    class MockUser:
        def __init__(self):
            self.email = "test@example.com"
        def is_pro_active(self):
            return True
    
    def get_current_user():
        return MockUser()
    
    def get_db():
        return None
    
    def Depends(func):
        return func()

router = APIRouter()

# Initialize service
professional_service = ProfessionalOutputService() if SERVICE_AVAILABLE else None

class ProfessionalPDFRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = ""
    template: Optional[str] = "executive_compact"
    ats_optimize: Optional[bool] = True

class ProfessionalDOCXRequest(BaseModel):
    resume_text: str
    template: Optional[str] = "executive_compact"

class ATSScoreRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = ""

@router.post("/generate-pdf")
async def generate_professional_pdf(
    request: ProfessionalPDFRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate professional ATS-optimized PDF"""
    try:
        if not SERVICE_AVAILABLE or not professional_service:
            raise HTTPException(status_code=503, detail="Professional output service not available")
        
        # Only one template supported
        if request.template != 'executive_compact':
            request.template = 'executive_compact'
        
        # Generate professional PDF
        result, ats_score = professional_service.generate_professional_pdf(
            resume_text=request.resume_text,
            job_description=request.job_description,
            template=request.template,
            ats_optimize=request.ats_optimize
        )

        if result['success']:
            headers = {
                "Content-Disposition": f"attachment; filename=professional_resume_{request.template}.pdf",
                "X-Template-Used": result['template_used']
            }
            if ats_score:
                headers["X-ATS-Score"] = str(ats_score.get('total_score', ''))
            return Response(
                content=result['pdf_content'],
                media_type="application/pdf",
                headers=headers
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'PDF generation failed'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/generate-docx")
async def generate_professional_docx(
    request: ProfessionalDOCXRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate professional DOCX document"""
    try:
        if not SERVICE_AVAILABLE or not professional_service:
            raise HTTPException(status_code=503, detail="Professional output service not available")
        
        # Only one template supported
        if request.template != 'executive_compact':
            request.template = 'executive_compact'
        
        # Generate professional DOCX
        result = professional_service.generate_professional_docx(
            resume_text=request.resume_text,
            template=request.template
        )

        if result['success']:
            return Response(
                content=result['docx_content'],
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f"attachment; filename=professional_resume_{request.template}.docx",
                    "X-Template-Used": result['template_used']
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'DOCX generation failed'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")

@router.post("/ats-score")
async def calculate_ats_score(
    request: ATSScoreRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate ATS compatibility score"""
    try:
        if not SERVICE_AVAILABLE or not professional_service:
            raise HTTPException(status_code=503, detail="Professional output service not available")
        
        # Calculate ATS score
        ats_results = professional_service.ats_scorer.calculate_ats_score(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        return {
            "success": True,
            "ats_score": ats_results['total_score'],
            "grade": ats_results['grade'],
            "components": ats_results['components'],
            "recommendations": ats_results['recommendations']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate ATS score: {str(e)}")

@router.get("/templates")
async def get_available_templates():
    """Get list of available professional templates"""
    try:
        if not SERVICE_AVAILABLE or not professional_service:
            return {
                "success": False,
                "templates": [],
                "error": "Professional output service not available"
            }
        
        templates = professional_service.get_available_templates()
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        return {
            "success": False,
            "templates": [],
            "error": str(e)
        }

@router.get("/test")
async def test_professional_output():
    """Test professional output service"""
    return {
        "status": "ok",
        "message": "Professional output service is ready!",
        "service_available": SERVICE_AVAILABLE,
        "features": {
            "pdf_generation": SERVICE_AVAILABLE,
            "docx_generation": SERVICE_AVAILABLE,
            "ats_scoring": SERVICE_AVAILABLE,
            "template_engine": SERVICE_AVAILABLE
        }
    }
