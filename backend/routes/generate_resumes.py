from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import asyncio
import json
from utils.gpt_prompt import GPTProcessor
from utils.resume_editor import ResumeEditor
from utils.langchain_processor import LangChainResumeProcessor
from utils.resume_diff import ResumeDiffAnalyzer
from models.user import TailoringMode, User
from utils.auth import AuthManager
from services.advanced_formatting_service import (
    AdvancedFormattingService,
    FormattingOptions,
    FormattingTemplate,
    ColorScheme,
    FontFamily
)
from services.job_specific_templates import JobSpecificTemplateService

router = APIRouter()

# Initialize processors
gpt_processor = GPTProcessor()  # Updated variable name
resume_editor = ResumeEditor()
langchain_processor = LangChainResumeProcessor()
diff_analyzer = ResumeDiffAnalyzer()
fallback_processor = GPTProcessor()  # Fallback for legacy mode
advanced_formatting_service = AdvancedFormattingService()  # Advanced formatting service
job_specific_template_service = JobSpecificTemplateService()  # Job-specific template service

class GenerateRequest(BaseModel):
    file_id: str
    jobs: List[dict]
    output_format: str = "pdf"  # "pdf" or "docx"
    tailoring_mode: Optional[TailoringMode] = TailoringMode.LIGHT  # Default to Light mode
    # Advanced formatting options (Pro only)
    formatting_template: Optional[str] = FormattingTemplate.STANDARD.value
    color_scheme: Optional[str] = ColorScheme.CLASSIC_BLUE.value
    font_family: Optional[str] = FontFamily.HELVETICA.value
    font_size: Optional[int] = 10
    use_advanced_formatting: Optional[bool] = False
    # Job-specific template options (Pro only)
    use_job_specific_template: Optional[bool] = False
    job_category: Optional[str] = None  # e.g., "software_engineer", "data_scientist"

class ResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str
    job_url: Optional[str] = ""
    use_rag: Optional[bool] = True  # Enable RAG by default
    compare_versions: Optional[bool] = True  # Enable diff analysis
    tailoring_mode: Optional[TailoringMode] = TailoringMode.LIGHT  # Default to Light mode
    optional_sections: Optional[Dict[str, Any]] = {
        "includeSummary": False,
        "includeSkills": False,
        "includeEducation": False,
        "educationDetails": {
            "degree": "",
            "institution": "",
            "year": "",
            "gpa": ""
        }
    }
    # Advanced formatting options (Pro only)
    formatting_template: Optional[str] = FormattingTemplate.STANDARD.value
    color_scheme: Optional[str] = ColorScheme.CLASSIC_BLUE.value
    font_family: Optional[str] = FontFamily.HELVETICA.value
    font_size: Optional[int] = 10
    use_advanced_formatting: Optional[bool] = False
    generate_pdf: Optional[bool] = False  # Whether to generate PDF with advanced formatting
    # Job-specific template options (Pro only)
    use_job_specific_template: Optional[bool] = False
    job_category: Optional[str] = None  # e.g., "software_engineer", "data_scientist"

class DiffAnalysisRequest(BaseModel):
    original_resume: str
    tailored_resume: str
    job_title: Optional[str] = ""

@router.post("/generate-resumes")
async def generate_tailored_resumes(request: GenerateRequest, user: User = Depends(AuthManager.verify_token)):
    """
    Generate tailored resumes for multiple job descriptions with tailoring mode support
    """
    try:
        # Validate input - check batch size limits based on subscription tier
        user_limits = user.get_usage_limits_new()
        max_batch_jobs = user_limits.get("bulk_jobs", 10)
        
        if len(request.jobs) > max_batch_jobs:
            tier_name = "Pro" if user.is_pro_active() else "Free"
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {max_batch_jobs} jobs allowed for {tier_name} users. Upgrade to Pro for up to 25 jobs per batch."
            )
        
        if request.output_format not in ["pdf", "docx"]:
            raise HTTPException(
                status_code=400,
                detail="Output format must be 'pdf' or 'docx'"
            )
        
        # Validate tailoring mode access (Pro users only for Heavy mode)
        effective_tailoring_mode = request.tailoring_mode or TailoringMode.LIGHT
        tailoring_mode_fallback = False
        tailoring_mode_fallback_reason = None
        
        # Enforce Pro-only access for Heavy tailoring mode
        if effective_tailoring_mode == TailoringMode.HEAVY and not user.is_pro_active():
            print(f"User {user.email} attempted Heavy tailoring without Pro subscription, falling back to Light mode")
            effective_tailoring_mode = TailoringMode.LIGHT
            tailoring_mode_fallback = True
            tailoring_mode_fallback_reason = "Heavy tailoring requires Pro subscription"
        
        # Log tailoring mode selection for debugging
        print(f"Bulk generation - Tailoring mode - Requested: {request.tailoring_mode}, Effective: {effective_tailoring_mode}, User Pro: {user.is_pro_active()}")
        
        # Get original resume text
        resume_file_path = f"uploads/{request.file_id}"
        if not os.path.exists(resume_file_path):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        original_resume_text = resume_editor.extract_text_from_file(resume_file_path)
        if not original_resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        generated_resumes = []
        
        for i, job in enumerate(request.jobs):
            if job.get("status") != "success" or not job.get("job_description"):
                continue
                
            try:
                # Extract job title from URL or use generic title
                job_title = f"Job_{i+1}"
                if "linkedin.com" in job.get("url", ""):
                    job_title = f"LinkedIn_Job_{i+1}"
                elif "indeed.com" in job.get("url", ""):
                    job_title = f"Indeed_Job_{i+1}"
                elif "greenhouse" in job.get("url", ""):
                    job_title = f"Greenhouse_Job_{i+1}"
                
                # Use GPT to tailor the resume with effective tailoring mode
                tailored_resume_text = gpt_processor.tailor_resume(
                    original_resume_text, 
                    job["job_description"], 
                    job_title,
                    {"includeSummary": False, "includeSkills": False, "includeEducation": False, "educationDetails": {}},  # Default to no optional sections
                    effective_tailoring_mode
                )
                
                if not tailored_resume_text:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_url": job.get("url", ""),
                        "status": "failed",
                        "error": "Failed to generate tailored resume with GPT"
                    })
                    continue
                
                # Generate output file
                output_filename = f"{uuid.uuid4()}_{job_title}.{request.output_format}"
                output_path = f"outputs/{output_filename}"
                
                # Create the tailored resume file
                if request.output_format == "pdf":
                    # Check if job-specific template is requested and user is Pro
                    if request.use_job_specific_template and user.is_pro_active() and request.job_category:
                        # Validate job-specific template request
                        is_valid, validation_message = job_specific_template_service.validate_job_specific_request(
                            request.job_category,
                            request.formatting_template,
                            user.is_pro_active()
                        )
                        
                        if is_valid:
                            # Create formatting options for job-specific template
                            formatting_options = FormattingOptions(
                                template=FormattingTemplate(request.formatting_template),
                                color_scheme=ColorScheme(request.color_scheme),
                                font_family=FontFamily(request.font_family),
                                font_size=request.font_size
                            )
                            
                            # Use job-specific template
                            success = job_specific_template_service.create_job_specific_resume(
                                tailored_resume_text,
                                request.job_category,
                                request.formatting_template,
                                formatting_options,
                                output_path,
                                job_title
                            )
                            
                            # Fallback to advanced formatting if job-specific fails
                            if not success:
                                success = advanced_formatting_service.create_advanced_formatted_resume(
                                    tailored_resume_text, formatting_options, output_path, job_title
                                )
                        else:
                            # Fallback to advanced formatting if validation fails
                            formatting_options = FormattingOptions(
                                template=FormattingTemplate(request.formatting_template),
                                color_scheme=ColorScheme(request.color_scheme),
                                font_family=FontFamily(request.font_family),
                                font_size=request.font_size
                            )
                            success = advanced_formatting_service.create_advanced_formatted_resume(
                                tailored_resume_text, formatting_options, output_path, job_title
                            )
                    
                    # Check if advanced formatting is requested and user is Pro
                    elif request.use_advanced_formatting and user.is_pro_active():
                        # Validate formatting options
                        is_valid, validation_message = advanced_formatting_service.validate_formatting_request(
                            request.formatting_template,
                            request.color_scheme,
                            request.font_family,
                            user.is_pro_active()
                        )
                        
                        if is_valid:
                            # Create formatting options
                            formatting_options = FormattingOptions(
                                template=FormattingTemplate(request.formatting_template),
                                color_scheme=ColorScheme(request.color_scheme),
                                font_family=FontFamily(request.font_family),
                                font_size=request.font_size
                            )
                            
                            # Use advanced formatting
                            success = advanced_formatting_service.create_advanced_formatted_resume(
                                tailored_resume_text, formatting_options, output_path, job_title
                            )
                            
                            # Fallback to standard if advanced formatting fails
                            if not success:
                                success = advanced_formatting_service.create_standard_formatted_resume(
                                    tailored_resume_text, output_path, job_title
                                )
                        else:
                            # Fallback to standard formatting if validation fails
                            success = advanced_formatting_service.create_standard_formatted_resume(
                                tailored_resume_text, output_path, job_title
                            )
                    else:
                        # Use standard PDF generation for Free users or when advanced formatting not requested
                        if user.is_pro_active():
                            # FORCE USE OF UPDATED REFERENCE FORMAT - bypass advanced formatting
                            # Use our updated ResumeEditor method that matches the reference format
                            success = resume_editor.create_tailored_resume_pdf(
                                tailored_resume_text, output_path, job_title
                            )
                            
                            # Only use advanced formatting as fallback if our method fails
                            if not success and request.use_advanced_formatting:
                                # Pro user requested advanced formatting but with standard template
                                success = advanced_formatting_service.create_standard_formatted_resume(
                                    tailored_resume_text, output_path, job_title
                                )
                else:  # docx
                    success = resume_editor.create_tailored_resume_docx(
                        tailored_resume_text, output_path, job_title
                    )
                
                if success:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_title": job_title,
                        "job_url": job.get("url", ""),
                        "status": "success",
                        "filename": output_filename,
                        "download_url": f"/api/download/{output_filename}",
                        "preview": tailored_resume_text[:300] + "..." if len(tailored_resume_text) > 300 else tailored_resume_text
                    })
                else:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_url": job.get("url", ""),
                        "status": "failed",
                        "error": "Failed to create output file"
                    })
                    
            except Exception as e:
                generated_resumes.append({
                    "job_id": job.get("id", i+1),
                    "job_url": job.get("url", ""),
                    "status": "failed",
                    "error": str(e)
                })
        
        successful_resumes = [r for r in generated_resumes if r["status"] == "success"]
        
        return JSONResponse({
            "message": f"Generated {len(successful_resumes)} tailored resumes",
            "total_jobs": len(request.jobs),
            "successful_generations": len(successful_resumes),
            "failed_generations": len(generated_resumes) - len(successful_resumes),
            "tailoring_mode_requested": request.tailoring_mode.value if request.tailoring_mode else "light",
            "tailoring_mode_used": effective_tailoring_mode.value,
            "tailoring_mode_fallback": tailoring_mode_fallback,
            "tailoring_mode_fallback_reason": tailoring_mode_fallback_reason,
            "resumes": generated_resumes
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resumes: {str(e)}")

@router.get("/download/{filename}")
async def download_resume(filename: str):
    """
    Download a generated resume file
    """
    try:
        file_path = f"outputs/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type based on file extension
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        elif filename.endswith('.docx'):
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/list-generated")
async def list_generated_resumes():
    """
    List all generated resume files
    """
    try:
        if not os.path.exists("outputs"):
            return JSONResponse({"files": []})
        
        files = []
        for filename in os.listdir("outputs"):
            if filename.endswith(('.pdf', '.docx')):
                file_path = f"outputs/{filename}"
                file_stats = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created": file_stats.st_ctime,
                    "download_url": f"/api/download/{filename}"
                })
        
        return JSONResponse({"files": files})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.post("/tailor")
async def tailor_resume(request: ResumeRequest, user: User = Depends(AuthManager.verify_token)):
    """Enhanced resume tailoring with LangChain RAG, diff analysis, and tailoring mode selection"""
    try:
        # Validate tailoring mode access (Pro users only for Heavy mode)
        effective_tailoring_mode = request.tailoring_mode or TailoringMode.LIGHT
        tailoring_mode_fallback = False
        tailoring_mode_fallback_reason = None
        
        # Enforce Pro-only access for Heavy tailoring mode
        if effective_tailoring_mode == TailoringMode.HEAVY and not user.is_pro_active():
            print(f"User {user.email} attempted Heavy tailoring without Pro subscription, falling back to Light mode")
            effective_tailoring_mode = TailoringMode.LIGHT
            tailoring_mode_fallback = True
            tailoring_mode_fallback_reason = "Heavy tailoring requires Pro subscription"
        
        # Log tailoring mode selection for debugging
        print(f"Tailoring mode - Requested: {request.tailoring_mode}, Effective: {effective_tailoring_mode}, User Pro: {user.is_pro_active()}")
        
        # Load existing job vector store
        langchain_processor.load_job_vectorstore()
        
        if request.use_rag:
            # Use LangChain RAG-enhanced processing with tailoring mode
            result = langchain_processor.tailor_resume_with_rag(
                resume_text=request.resume_text,
                job_description=request.job_description,
                job_title=request.job_title,
                optional_sections=request.optional_sections,
                tailoring_mode=effective_tailoring_mode
            )
            
            if not result:
                # Fallback to standard GPT processing
                print("RAG processing failed, using fallback...")
                tailored_resume = fallback_processor.tailor_resume(
                    request.resume_text, 
                    request.job_description, 
                    request.job_title,
                    request.optional_sections,
                    effective_tailoring_mode
                )
                result = {
                    "session_id": "fallback",
                    "tailored_resume": tailored_resume,
                    "similar_jobs_found": 0,
                    "rag_insights": [],
                    "processing_steps": ["Used fallback GPT processing"]
                }
        else:
            # Use standard GPT processing with tailoring mode
            tailored_resume = fallback_processor.tailor_resume(
                request.resume_text, 
                request.job_description, 
                request.job_title,
                request.optional_sections,
                effective_tailoring_mode
            )
            result = {
                "session_id": "standard",
                "tailored_resume": tailored_resume,
                "similar_jobs_found": 0,
                "rag_insights": [],
                "processing_steps": ["Used standard GPT processing"]
            }

        # Perform diff analysis if requested
        diff_analysis = None
        if request.compare_versions and result.get("tailored_resume"):
            diff_analysis = diff_analyzer.analyze_resume_diff(
                original_text=request.resume_text,
                tailored_text=result["tailored_resume"],
                job_title=request.job_title
            )

        # Store job description in vector store for future RAG
        if request.job_description and request.job_url:
            job_data = [{
                "id": result.get("session_id", "unknown"),
                "job_description": request.job_description,
                "job_title": request.job_title,
                "url": request.job_url
            }]
            langchain_processor.initialize_job_vectorstore(job_data)

        response_data = {
            "success": True,
            "session_id": result.get("session_id"),
            "tailored_resume": result.get("tailored_resume"),
            "processing_mode": "RAG-Enhanced" if request.use_rag else "Standard",
            "tailoring_mode_requested": request.tailoring_mode.value if request.tailoring_mode else "light",
            "tailoring_mode_used": effective_tailoring_mode.value,
            "tailoring_mode_fallback": tailoring_mode_fallback,
            "tailoring_mode_fallback_reason": "Heavy tailoring requires Pro subscription" if tailoring_mode_fallback else None,
            "rag_insights": {
                "similar_jobs_found": result.get("similar_jobs_found", 0),
                "insights": result.get("rag_insights", []),
                "processing_steps": result.get("processing_steps", [])
            }
        }

        # Add diff analysis if performed
        if diff_analysis:
            response_data["diff_analysis"] = diff_analysis
            response_data["diff_report"] = diff_analyzer.create_diff_report(diff_analysis)

        # Generate PDF with advanced formatting if requested
        pdf_info = None
        if request.generate_pdf and result.get("tailored_resume"):
            try:
                # Generate unique filename
                pdf_filename = f"{uuid.uuid4()}_{request.job_title.replace(' ', '_')}.pdf"
                pdf_path = f"outputs/{pdf_filename}"
                
                # Check if job-specific template is requested and user is Pro
                if request.use_job_specific_template and user.is_pro_active() and request.job_category:
                    # Validate job-specific template request
                    is_valid, validation_message = job_specific_template_service.validate_job_specific_request(
                        request.job_category,
                        request.formatting_template,
                        user.is_pro_active()
                    )
                    
                    if is_valid:
                        # Create formatting options for job-specific template
                        formatting_options = FormattingOptions(
                            template=FormattingTemplate(request.formatting_template),
                            color_scheme=ColorScheme(request.color_scheme),
                            font_family=FontFamily(request.font_family),
                            font_size=request.font_size
                        )
                        
                        # Use job-specific template
                        pdf_success = job_specific_template_service.create_job_specific_resume(
                            result["tailored_resume"],
                            request.job_category,
                            request.formatting_template,
                            formatting_options,
                            pdf_path,
                            request.job_title
                        )
                        
                        # Fallback to advanced formatting if job-specific fails
                        if not pdf_success:
                            pdf_success = advanced_formatting_service.create_advanced_formatted_resume(
                                result["tailored_resume"], formatting_options, pdf_path, request.job_title
                            )
                    else:
                        # Fallback to advanced formatting if validation fails
                        formatting_options = FormattingOptions(
                            template=FormattingTemplate(request.formatting_template),
                            color_scheme=ColorScheme(request.color_scheme),
                            font_family=FontFamily(request.font_family),
                            font_size=request.font_size
                        )
                        pdf_success = advanced_formatting_service.create_advanced_formatted_resume(
                            result["tailored_resume"], formatting_options, pdf_path, request.job_title
                        )
                
                # Check if advanced formatting is requested and user is Pro
                elif request.use_advanced_formatting and user.is_pro_active():
                    # Validate formatting options
                    is_valid, validation_message = advanced_formatting_service.validate_formatting_request(
                        request.formatting_template,
                        request.color_scheme,
                        request.font_family,
                        user.is_pro_active()
                    )
                    
                    if is_valid:
                        # Create formatting options
                        formatting_options = FormattingOptions(
                            template=FormattingTemplate(request.formatting_template),
                            color_scheme=ColorScheme(request.color_scheme),
                            font_family=FontFamily(request.font_family),
                            font_size=request.font_size
                        )
                        
                        # Use advanced formatting
                        pdf_success = advanced_formatting_service.create_advanced_formatted_resume(
                            result["tailored_resume"], formatting_options, pdf_path, request.job_title
                        )
                        
                        # Fallback to standard if advanced formatting fails
                        if not pdf_success:
                            pdf_success = advanced_formatting_service.create_standard_formatted_resume(
                                result["tailored_resume"], pdf_path, request.job_title
                            )
                    else:
                        # Fallback to standard formatting if validation fails
                        pdf_success = advanced_formatting_service.create_standard_formatted_resume(
                            result["tailored_resume"], pdf_path, request.job_title
                        )
                else:
                    # Use standard PDF generation for Free users or when advanced formatting not requested
                    if user.is_pro_active() and request.use_advanced_formatting:
                        # Pro user requested advanced formatting but with standard template
                        pdf_success = advanced_formatting_service.create_standard_formatted_resume(
                            result["tailored_resume"], pdf_path, request.job_title
                        )
                    else:
                        # Use existing resume editor for Free users
                        pdf_success = resume_editor.create_tailored_resume_pdf(
                            result["tailored_resume"], pdf_path, request.job_title
                        )
                
                if pdf_success:
                    pdf_info = {
                        "filename": pdf_filename,
                        "download_url": f"/api/resumes/download/{pdf_filename}",
                        "formatting_template": request.formatting_template if request.use_advanced_formatting else "standard",
                        "advanced_formatting_used": request.use_advanced_formatting and user.is_pro_active()
                    }
                else:
                    pdf_info = {
                        "error": "Failed to generate PDF",
                        "advanced_formatting_used": False
                    }
                    
            except Exception as e:
                pdf_info = {
                    "error": f"PDF generation failed: {str(e)}",
                    "advanced_formatting_used": False
                }
        
        # Add PDF info to response if generated
        if pdf_info:
            response_data["pdf"] = pdf_info

        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"Error in tailor_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume tailoring failed: {str(e)}")

@router.post("/analyze-diff")
async def analyze_resume_diff(request: DiffAnalysisRequest):
    """Standalone diff analysis between two resume versions"""
    try:
        diff_analysis = diff_analyzer.analyze_resume_diff(
            original_text=request.original_resume,
            tailored_text=request.tailored_resume,
            job_title=request.job_title
        )
        
        diff_report = diff_analyzer.create_diff_report(diff_analysis)
        
        return JSONResponse(content={
            "success": True,
            "diff_analysis": diff_analysis,
            "diff_report": diff_report
        })
        
    except Exception as e:
        print(f"Error in analyze_resume_diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diff analysis failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Retrieve session history and analysis"""
    try:
        session_data = langchain_processor.get_session_history(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse(content={
            "success": True,
            "session_data": session_data
        })
        
    except Exception as e:
        print(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session retrieval failed: {str(e)}")

@router.get("/sessions")
async def get_all_sessions():
    """Get all session history"""
    try:
        all_sessions = langchain_processor.get_all_sessions()
        
        return JSONResponse(content={
            "success": True,
            "total_sessions": len(all_sessions),
            "sessions": all_sessions
        })
        
    except Exception as e:
        print(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sessions retrieval failed: {str(e)}")

@router.post("/initialize-rag")
async def initialize_rag_system(job_descriptions: list):
    """Initialize or update the RAG system with job descriptions"""
    try:
        success = langchain_processor.initialize_job_vectorstore(job_descriptions)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"RAG system initialized with {len(job_descriptions)} job descriptions"
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize RAG system")
            
    except Exception as e:
        print(f"Error initializing RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG initialization failed: {str(e)}")

@router.get("/rag-status")
async def get_rag_status():
    """Get status of RAG system"""
    try:
        vector_store_exists = langchain_processor.load_job_vectorstore()
        
        return JSONResponse(content={
            "success": True,
            "rag_available": vector_store_exists,
            "vector_store_path": "vector_stores/job_descriptions"
        })
        
    except Exception as e:
        print(f"Error checking RAG status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG status check failed: {str(e)}")

@router.get("/job-categories")
async def get_job_categories(user: User = Depends(AuthManager.verify_token)):
    """Get available job categories for job-specific templates"""
    try:
        categories = job_specific_template_service.get_available_job_categories(user.is_pro_active())
        
        return JSONResponse(content={
            "success": True,
            "categories": categories,
            "user_tier": "pro" if user.is_pro_active() else "free",
            "total_categories": len(categories)
        })
        
    except Exception as e:
        print(f"Error getting job categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job categories: {str(e)}")

@router.get("/job-categories/{category}/templates")
async def get_job_category_templates(category: str, user: User = Depends(AuthManager.verify_token)):
    """Get all template variations for a specific job category"""
    try:
        templates = job_specific_template_service.get_job_category_templates(category, user.is_pro_active())
        
        return JSONResponse(content={
            "success": True,
            "templates": templates,
            "user_tier": "pro" if user.is_pro_active() else "free"
        })
        
    except Exception as e:
        print(f"Error getting job category templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates for category: {str(e)}")

@router.post("/suggest-job-category")
async def suggest_job_category(request: dict, user: User = Depends(AuthManager.verify_token)):
    """Suggest job category based on job title"""
    try:
        job_title = request.get("job_title", "")
        if not job_title:
            raise HTTPException(status_code=400, detail="job_title is required")
        
        suggested_category = job_specific_template_service.get_job_category_by_title(job_title)
        
        response_data = {
            "success": True,
            "job_title": job_title,
            "suggested_category": suggested_category.value if suggested_category else None,
            "user_tier": "pro" if user.is_pro_active() else "free"
        }
        
        # If a category is suggested and user is Pro, include template info
        if suggested_category and user.is_pro_active():
            templates = job_specific_template_service.get_job_category_templates(
                suggested_category.value, user.is_pro_active()
            )
            response_data["category_info"] = templates
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error suggesting job category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest job category: {str(e)}") 