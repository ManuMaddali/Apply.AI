from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import time
import os
import zipfile
import tempfile
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from utils.job_scraper import JobScraper
from utils.langchain_processor import LangChainResumeProcessor
from utils.gpt_prompt import GPTProcessor
from utils.resume_diff import ResumeDiffAnalyzer
from utils.resume_editor import ResumeEditor
from models.user import TailoringMode, User
from services.subscription_service import SubscriptionService, UsageType
from config.database import get_db
from utils.auth import get_current_user
from fastapi import Depends
from sqlalchemy.orm import Session
from services.advanced_formatting_service import (
    AdvancedFormattingService,
    FormattingOptions,
    FormattingTemplate,
    ColorScheme,
    FontFamily
)

router = APIRouter()

# Initialize processors
job_scraper = JobScraper()
langchain_processor = LangChainResumeProcessor()
fallback_processor = GPTProcessor()
diff_analyzer = ResumeDiffAnalyzer()
resume_editor = ResumeEditor()
advanced_formatting_service = AdvancedFormattingService()  # Advanced formatting service

# In-memory storage for batch jobs (consider using Redis or a database for production)
batch_jobs: Dict[str, Any] = {}
batch_results: Dict[str, List[Dict[str, Any]]] = {}

class BatchProcessRequest(BaseModel):
    resume_text: str
    job_urls: List[str]
    use_rag: Optional[bool] = True
    output_format: Optional[str] = "text"  # "text" or "files"
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
    cover_letter_options: Optional[Dict[str, Any]] = {
        "includeCoverLetter": False,
        "coverLetterDetails": {
            "tone": "professional",
            "emphasize": "experience",
            "additionalInfo": ""
        }
    }
    # Advanced formatting options (Pro only)
    formatting_template: Optional[str] = FormattingTemplate.STANDARD.value
    color_scheme: Optional[str] = ColorScheme.CLASSIC_BLUE.value
    font_family: Optional[str] = FontFamily.HELVETICA.value
    font_size: Optional[int] = 10
    use_advanced_formatting: Optional[bool] = False

class PDFGenerateRequest(BaseModel):
    resume_text: str
    job_title: str
    filename: Optional[str] = None

class CoverLetterPDFRequest(BaseModel):
    cover_letter_text: str
    job_title: str
    filename: Optional[str] = None

class ZIPGenerateRequest(BaseModel):
    resumes: List[Dict[str, Any]]
    batch_id: str
    include_cover_letters: Optional[bool] = False

def generate_pdf_from_text(
    resume_text: str, 
    job_title: str, 
    formatting_options: Optional[FormattingOptions] = None,
    use_advanced_formatting: bool = False,
    is_pro_user: bool = False
) -> BytesIO:
    """Generate PDF using advanced formatting service or ResumeEditor for better formatting"""
    try:
        # Create temporary file for PDF
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)  # Close the file descriptor
        
        success = False
        
        # Use advanced formatting if requested and user is Pro
        if use_advanced_formatting and is_pro_user and formatting_options:
            # Use advanced formatting service
            success = advanced_formatting_service.create_advanced_formatted_resume(
                resume_text, formatting_options, temp_path, job_title
            )
            
            # Fallback to standard advanced formatting if specific template fails
            if not success:
                success = advanced_formatting_service.create_standard_formatted_resume(
                    resume_text, temp_path, job_title
                )
        elif use_advanced_formatting and is_pro_user:
            # Use standard advanced formatting for Pro users without specific options
            success = advanced_formatting_service.create_standard_formatted_resume(
                resume_text, temp_path, job_title
            )
        
        # Fallback to ResumeEditor if advanced formatting not used or failed
        if not success:
            success = resume_editor.create_tailored_resume_pdf(
                tailored_text=resume_text,
                output_path=temp_path,
                job_title=job_title
            )
        
        if not success:
            raise Exception("Failed to create PDF with all available methods")
        
        # Read the PDF into a BytesIO buffer
        buffer = BytesIO()
        with open(temp_path, 'rb') as f:
            buffer.write(f.read())
        
        # Clean up temp file
        os.unlink(temp_path)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback to basic PDF if all methods fail
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = [
            Paragraph(f"Resume for: {job_title}", styles['Title']),
            Paragraph("Error generating formatted PDF. Content:", styles['Normal']),
            Spacer(1, 12),
            Paragraph(resume_text[:1000] + "...", styles['Normal'])
        ]
        doc.build(content)
        buffer.seek(0)
        return buffer

def generate_cover_letter_pdf(cover_letter_text: str, job_title: str) -> BytesIO:
    """Generate a professional cover letter PDF"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch, leftMargin=1*inch, rightMargin=1*inch)
        
        # Create custom styles
        styles = getSampleStyleSheet()
        
        # Header style
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=24,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        # Date style
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=24,
            alignment=2,  # Right alignment
        )
        
        # Body style
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0,
            lineHeight=14
        )
        
        # Title style
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=18,
            fontName='Helvetica-Bold',
            alignment=1  # Center alignment
        )
        
        # Build content
        content = []
        
        # Date
        current_date = datetime.now().strftime("%B %d, %Y")
        content.append(Paragraph(current_date, date_style))
        
        # Title
        content.append(Paragraph(f"Cover Letter - {job_title}", title_style))
        
        # Cover letter content
        # Split the cover letter text into paragraphs
        paragraphs = cover_letter_text.split('\n\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Clean up the paragraph text
                clean_paragraph = paragraph.strip().replace('\n', ' ')
                content.append(Paragraph(clean_paragraph, body_style))
        
        # Build the PDF
        doc.build(content)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Cover letter PDF generation error: {e}")
        # Fallback to basic PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = [
            Paragraph(f"Cover Letter for: {job_title}", styles['Title']),
            Spacer(1, 12),
            Paragraph(cover_letter_text[:2000] + "...", styles['Normal'])
        ]
        doc.build(content)
        buffer.seek(0)
        return buffer

class BatchJobStatus:
    def __init__(self, batch_id: str, total_jobs: int, optional_sections: Optional[Dict[str, Any]] = None, cover_letter_options: Optional[Dict[str, Any]] = None):
        self.batch_id = batch_id
        self.state = "pending"  # pending, processing, completed, failed
        self.total = total_jobs
        self.completed = 0
        self.failed = 0
        self.current_job = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []
        self.optional_sections = optional_sections or {
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
        self.cover_letter_options = cover_letter_options or {
            "includeCoverLetter": False,
            "coverLetterDetails": {
                "tone": "professional",
                "emphasize": "experience",
                "additionalInfo": ""
            }
        }

async def process_single_job(resume_text: str, job_url: str, use_rag: bool, optional_sections: Dict[str, Any], cover_letter_options: Dict[str, Any], batch_id: str, job_index: int, tailoring_mode: TailoringMode = TailoringMode.LIGHT) -> Dict[str, Any]:
    """Process a single job and return the result"""
    try:
        # Update current job in status
        if batch_id in batch_jobs:
            batch_jobs[batch_id].current_job = f"Job {job_index + 1}: {job_url[:50]}..."
            batch_jobs[batch_id].updated_at = datetime.now()

        # Scrape job description
        job_description = job_scraper.scrape_job_description(job_url)
        if not job_description:
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": f"Job_{job_index + 1}",
                "status": "failed",
                "error": "Failed to scrape job description",
                "tailored_resume": None,
                "cover_letter": None
            }

        # Extract job title
        job_title = job_scraper.extract_job_title(job_url) or f"Job_{job_index + 1}"

        # Tailor resume using RAG or fallback with tailoring mode
        if use_rag:
            langchain_processor.load_job_vectorstore()
            rag_result = langchain_processor.tailor_resume_with_rag(
                resume_text=resume_text,
                job_description=job_description,
                job_title=job_title,
                optional_sections=optional_sections,
                tailoring_mode=tailoring_mode
            )
            
            if rag_result:
                tailored_resume = rag_result.get("tailored_resume")
                similar_jobs_found = rag_result.get("similar_jobs_found", 0)
            else:
                # Fallback to standard processing
                tailored_resume = fallback_processor.tailor_resume(
                    resume_text, job_description, job_title, optional_sections, tailoring_mode
                )
                similar_jobs_found = 0
        else:
            tailored_resume = fallback_processor.tailor_resume(
                resume_text, job_description, job_title, optional_sections, tailoring_mode
            )
            similar_jobs_found = 0

        if not tailored_resume:
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": job_title,
                "status": "failed",
                "error": "Failed to generate tailored resume",
                "tailored_resume": None,
                "cover_letter": None
            }

        # Generate cover letter if requested
        cover_letter = None
        if cover_letter_options.get("includeCoverLetter", False):
            try:
                cover_letter = fallback_processor.generate_cover_letter(
                    resume_text=resume_text,
                    job_description=job_description,
                    job_title=job_title,
                    cover_letter_options=cover_letter_options
                )
            except Exception as e:
                print(f"Cover letter generation failed for job {job_index + 1}: {e}")
                # Don't fail the entire job if cover letter fails

        # Perform diff analysis
        diff_analysis = None
        try:
            diff_analysis = diff_analyzer.analyze_resume_diff(
                original_text=resume_text,
                tailored_text=tailored_resume,
                job_title=job_title
            )
        except Exception as e:
            print(f"Diff analysis failed for job {job_index + 1}: {e}")
            # Continue without diff analysis

        # Store job description for future RAG
        if job_description and job_url:
            job_data = [{
                "id": f"{batch_id}_{job_index}",
                "job_description": job_description,
                "job_title": job_title,
                "url": job_url
            }]
            langchain_processor.initialize_job_vectorstore(job_data)

        # Safely extract enhancement score
        enhancement_score = None
        if diff_analysis and isinstance(diff_analysis, dict):
            enhancement_data = diff_analysis.get("enhancement_score", {})
            if enhancement_data and isinstance(enhancement_data, dict):
                enhancement_score = enhancement_data.get("overall_score")

        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": job_title,
            "job_description": job_description,
            "status": "success",
            "tailored_resume": tailored_resume,
            "cover_letter": cover_letter,
            "similar_jobs_found": similar_jobs_found,
            "enhancement_score": enhancement_score,
            "diff_analysis": diff_analysis,
            "processing_time": time.time()
        }

    except Exception as e:
        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": f"Job_{job_index + 1}",
            "status": "failed",
            "error": str(e),
            "tailored_resume": None,
            "cover_letter": None
        }

async def process_batch_jobs(batch_id: str, resume_text: str, job_urls: List[str], use_rag: bool, output_format: str, optional_sections: Dict[str, Any], cover_letter_options: Dict[str, Any], tailoring_mode: TailoringMode = TailoringMode.LIGHT):
    """Background task to process all jobs in a batch"""
    try:
        batch_jobs[batch_id].state = "processing"
        batch_jobs[batch_id].updated_at = datetime.now()
        
        results = []
        
        # Process jobs sequentially (could be made parallel for better performance)
        for i, job_url in enumerate(job_urls):
            result = await process_single_job(resume_text, job_url, use_rag, optional_sections, cover_letter_options, batch_id, i, tailoring_mode)
            results.append(result)
            
            # Update progress
            if batch_id in batch_jobs:
                batch_jobs[batch_id].completed += 1
                if result["status"] == "failed":
                    batch_jobs[batch_id].failed += 1
                batch_jobs[batch_id].updated_at = datetime.now()
                batch_jobs[batch_id].results.append(result)

        # Store final results
        batch_results[batch_id] = results
        
        # Mark as completed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "completed"
            batch_jobs[batch_id].current_job = None
            batch_jobs[batch_id].updated_at = datetime.now()
            
    except Exception as e:
        # Mark as failed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "failed"
            batch_jobs[batch_id].current_job = f"Error: {str(e)}"
            batch_jobs[batch_id].updated_at = datetime.now()

@router.post("/process")
async def start_batch_processing(
    request: BatchProcessRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start batch processing of multiple job URLs"""
    try:
        # Validate input
        if len(request.job_urls) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 job URLs allowed")
        
        if len(request.job_urls) == 0:
            raise HTTPException(status_code=400, detail="At least one job URL is required")
        
        # Check if user is requesting cover letters and enforce Pro-only access
        subscription_service = SubscriptionService(db)
        if request.cover_letter_options and request.cover_letter_options.get("includeCoverLetter", False):
            can_use_cover_letters = await subscription_service.check_usage_limits(str(current_user.id), UsageType.COVER_LETTER)
            if not can_use_cover_letters.can_use:
                raise HTTPException(status_code=403, detail="Cover letters require Pro subscription")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Initialize batch status with default values for None parameters
        batch_status = BatchJobStatus(
            batch_id, 
            len(request.job_urls), 
            request.optional_sections or {},
            request.cover_letter_options or {}
        )
        batch_jobs[batch_id] = batch_status
        
        # Start background processing with default values for None parameters
        background_tasks.add_task(
            process_batch_jobs,
            batch_id,
            request.resume_text,
            request.job_urls,
            request.use_rag or False,
            request.output_format or "pdf",
            request.optional_sections or {},
            request.cover_letter_options or {}
        )
        
        return JSONResponse({
            "success": True,
            "batch_job_id": batch_id,
            "message": f"Batch processing started for {len(request.job_urls)} jobs",
            "status": {
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "current_job": batch_status.current_job
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@router.post("/generate-pdf")
async def generate_single_pdf(request: PDFGenerateRequest):
    """Generate a single PDF from resume text"""
    try:
        # Generate PDF (using standard formatting for single PDF endpoint)
        pdf_buffer = generate_pdf_from_text(
            request.resume_text, 
            request.job_title,
            formatting_options=None,
            use_advanced_formatting=False,
            is_pro_user=False
        )
        
        # Return PDF as response
        from fastapi.responses import Response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename or 'resume.pdf'}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/generate-cover-letter-pdf")
async def generate_cover_letter_pdf_endpoint(
    request: CoverLetterPDFRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a single cover letter PDF - Pro users only"""
    try:
        # Check Pro subscription for cover letter access
        subscription_service = SubscriptionService(db)
        can_use_cover_letters = await subscription_service.check_usage_limits(str(current_user.id), UsageType.COVER_LETTER)
        if not can_use_cover_letters.can_use:
            raise HTTPException(status_code=403, detail="Cover letters require Pro subscription")
        
        # Generate cover letter PDF
        pdf_buffer = generate_cover_letter_pdf(request.cover_letter_text, request.job_title)
        
        # Return PDF as response
        from fastapi.responses import Response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename or 'cover_letter.pdf'}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter PDF: {str(e)}")

@router.post("/generate-zip")
async def generate_zip_file(
    request: ZIPGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a ZIP file containing multiple resume PDFs with improved error handling"""
    zip_path = None
    try:
        # Check if user is requesting cover letters and enforce Pro-only access
        subscription_service = SubscriptionService(db)
        if request.include_cover_letters:
            can_use_cover_letters = await subscription_service.check_usage_limits(str(current_user.id), UsageType.COVER_LETTER)
            if not can_use_cover_letters.can_use:
                raise HTTPException(status_code=403, detail="Cover letters require Pro subscription")
        
        # Validate input
        if not request.resumes:
            raise HTTPException(status_code=400, detail="No resumes provided")
        
        if len(request.resumes) > 20:  # Safety limit
            raise HTTPException(status_code=400, detail="Too many resumes requested")
        
        # Create temporary file for ZIP
        import tempfile
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"batch_resumes_{request.batch_id[:8]}_{int(time.time())}.zip")
        
        successful_pdfs = 0
        successful_cover_letters = 0
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for i, resume_data in enumerate(request.resumes):
                try:
                    # Validate resume data
                    if not resume_data.get('resume_text'):
                        print(f"Skipping resume {i+1}: No resume text")
                        continue
                    
                    if not resume_data.get('job_title'):
                        resume_data['job_title'] = f"Resume_{i+1}"
                    
                    # Create safe filename base
                    job_title = resume_data['job_title']
                    safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
                    if not safe_title:
                        safe_title = f"Resume_{i+1}"
                    safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
                    
                    # Generate Resume PDF (using standard formatting for ZIP generation)
                    pdf_buffer = generate_pdf_from_text(
                        resume_data['resume_text'], 
                        resume_data['job_title'],
                        formatting_options=None,
                        use_advanced_formatting=False,
                        is_pro_user=False
                    )
                    
                    resume_filename = f"{i+1:02d}_{safe_title}_Resume.pdf"
                    zipf.writestr(resume_filename, pdf_buffer.getvalue())
                    successful_pdfs += 1
                    
                    # Generate Cover Letter PDF if available and requested
                    if request.include_cover_letters and resume_data.get('cover_letter'):
                        try:
                            cover_letter_buffer = generate_cover_letter_pdf(
                                resume_data['cover_letter'],
                                resume_data['job_title']
                            )
                            
                            cover_letter_filename = f"{i+1:02d}_{safe_title}_Cover_Letter.pdf"
                            zipf.writestr(cover_letter_filename, cover_letter_buffer.getvalue())
                            successful_cover_letters += 1
                        except Exception as e:
                            print(f"Error generating cover letter PDF for resume {i+1}: {e}")
                    
                    # Add summary file for this resume
                    summary_content = f"""Resume: {resume_data['job_title']}
Job URL: {resume_data.get('job_url', 'N/A')}
Enhancement Score: {resume_data.get('enhancement_score', 'N/A')}
Cover Letter: {'Included' if resume_data.get('cover_letter') and request.include_cover_letters else 'Not included'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: Successfully generated
"""
                    
                    summary_filename = f"{i+1:02d}_{safe_title}_Info.txt"
                    zipf.writestr(summary_filename, summary_content.encode('utf-8'))
                    
                except Exception as e:
                    print(f"Error processing resume {i+1}: {str(e)}")
                    # Add error info file instead
                    try:
                        error_content = f"""Resume: {resume_data.get('job_title', f'Resume_{i+1}')}
Job URL: {resume_data.get('job_url', 'N/A')}
Status: Failed to generate PDF
Error: {str(e)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                        error_filename = f"{i+1:02d}_ERROR_{resume_data.get('job_title', f'Resume_{i+1}')[:20]}.txt"
                        zipf.writestr(error_filename, error_content.encode('utf-8'))
                    except:
                        pass  # Skip if even error file creation fails
                    continue
            
            # Add batch summary
            batch_summary = f"""BATCH PROCESSING SUMMARY
========================
Batch ID: {request.batch_id}
Total Resumes Requested: {len(request.resumes)}
Successful Resume PDFs Generated: {successful_pdfs}
Successful Cover Letter PDFs Generated: {successful_cover_letters}
Cover Letters Requested: {'Yes' if request.include_cover_letters else 'No'}
Failed: {len(request.resumes) - successful_pdfs}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This ZIP file contains:
- {successful_pdfs} successfully generated PDF resume(s)
{f"- {successful_cover_letters} successfully generated cover letter PDF(s)" if request.include_cover_letters else ""}
- Info files with job details and enhancement scores
- Error logs for any failed generations
- This summary file

All resumes have been tailored using AI for specific job requirements.
RAG (Retrieval-Augmented Generation) and advanced diff analysis were applied.
{f"Cover letters have been personalized based on user preferences and job requirements." if request.include_cover_letters else ""}
"""
            zipf.writestr("BATCH_SUMMARY.txt", batch_summary.encode('utf-8'))
        
        # Verify ZIP file was created and has content
        if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
            raise Exception("ZIP file was not created properly")
        
        if successful_pdfs == 0:
            raise Exception("No PDFs were successfully generated")
        
        # Return ZIP file
        def cleanup_file():
            try:
                if os.path.exists(zip_path):
                    os.unlink(zip_path)
            except Exception as e:
                print(f"Error cleaning up file: {e}")
        
        background_tasks = BackgroundTasks()
        background_tasks.add_task(cleanup_file)
        
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"Apply_AI_Batch_{request.batch_id[:8]}.zip",
            background=background_tasks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if zip_path and os.path.exists(zip_path):
            try:
                os.unlink(zip_path)
            except:
                pass
        
        print(f"ZIP generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ZIP file: {str(e)}")

@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get the current status of a batch job"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        batch_status = batch_jobs[batch_id]
        
        return JSONResponse({
            "success": True,
            "batch_id": batch_id,
            "status": {
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "current_job": batch_status.current_job,
                "created_at": batch_status.created_at.isoformat(),
                "updated_at": batch_status.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")

@router.get("/results/{batch_id}")
async def get_batch_results(batch_id: str):
    """Get the results of a completed batch job"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        batch_status = batch_jobs[batch_id]
        
        # Return results from either batch_results or batch_status
        if batch_id in batch_results:
            results = batch_results[batch_id]
        else:
            results = batch_status.results
        
        return JSONResponse({
            "success": True,
            "batch_id": batch_id,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len([r for r in results if r.get("status") == "success"]),
                "failed": len([r for r in results if r.get("status") == "failed"]),
                "cover_letters_generated": len([r for r in results if r.get("cover_letter")])
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch results: {str(e)}")

@router.get("/jobs")
async def list_batch_jobs():
    """List all batch jobs (for admin/debugging)"""
    try:
        jobs_summary = []
        for batch_id, batch_status in batch_jobs.items():
            jobs_summary.append({
                "batch_id": batch_id,
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "created_at": batch_status.created_at.isoformat(),
                "updated_at": batch_status.updated_at.isoformat()
            })
        
        return JSONResponse({
            "success": True,
            "total_batches": len(jobs_summary),
            "batches": jobs_summary
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list batch jobs: {str(e)}")

@router.delete("/jobs/{batch_id}")
async def delete_batch_job(batch_id: str):
    """Delete a batch job and its results"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        # Remove from storage
        del batch_jobs[batch_id]
        if batch_id in batch_results:
            del batch_results[batch_id]
        
        return JSONResponse({
            "success": True,
            "message": f"Batch job {batch_id} deleted successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete batch job: {str(e)}")

@router.get("/download/{result_id}")
async def download_batch_result(result_id: str):
    """Download a specific result file (if files were generated)"""
    try:
        # This would be implemented when file generation is added
        # For now, return a placeholder response
        raise HTTPException(status_code=501, detail="File download not yet implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download result: {str(e)}") 