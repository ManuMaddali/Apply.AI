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
from utils.job_scraper import JobScraper
from utils.langchain_processor import LangChainResumeProcessor
from utils.gpt_prompt import GPTProcessor
from utils.resume_diff import ResumeDiffAnalyzer
from utils.resume_editor import ResumeEditor

router = APIRouter()

# Initialize processors
job_scraper = JobScraper()
langchain_processor = LangChainResumeProcessor()
fallback_processor = GPTProcessor()
diff_analyzer = ResumeDiffAnalyzer()
resume_editor = ResumeEditor()

# In-memory storage for batch jobs (in production, use Redis or database)
batch_jobs = {}
batch_results = {}

class BatchProcessRequest(BaseModel):
    resume_text: str
    job_urls: List[str]
    use_rag: Optional[bool] = True
    output_format: Optional[str] = "text"  # "text" or "files"

class PDFGenerateRequest(BaseModel):
    resume_text: str
    job_title: str
    filename: Optional[str] = None

class ZIPGenerateRequest(BaseModel):
    resumes: List[Dict[str, Any]]
    batch_id: str

def generate_pdf_from_text(resume_text: str, job_title: str) -> BytesIO:
    """Generate PDF from resume text using ReportLab"""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          topMargin=0.5*inch, bottomMargin=0.5*inch,
                          leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='black',
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor='black',
        spaceAfter=6,
        leftIndent=0,
        rightIndent=0
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='black',
        spaceAfter=8,
        spaceBefore=12,
        leftIndent=0
    )
    
    # Build content
    content = []
    
    # Add title
    content.append(Paragraph(f"Tailored Resume - {job_title}", title_style))
    content.append(Spacer(1, 12))
    
    # Process resume text
    lines = resume_text.split('\n')
    current_paragraph = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_paragraph:
                # Determine if this is a heading (short line, all caps, or ends with colon)
                if (len(current_paragraph) < 50 and 
                    (current_paragraph.isupper() or current_paragraph.endswith(':'))):
                    content.append(Paragraph(current_paragraph, heading_style))
                else:
                    content.append(Paragraph(current_paragraph, normal_style))
                current_paragraph = ""
            content.append(Spacer(1, 6))
        else:
            if current_paragraph:
                current_paragraph += " " + line
            else:
                current_paragraph = line
    
    # Add remaining paragraph
    if current_paragraph:
        if (len(current_paragraph) < 50 and 
            (current_paragraph.isupper() or current_paragraph.endswith(':'))):
            content.append(Paragraph(current_paragraph, heading_style))
        else:
            content.append(Paragraph(current_paragraph, normal_style))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

class BatchJobStatus:
    def __init__(self, batch_id: str, total_jobs: int):
        self.batch_id = batch_id
        self.state = "pending"  # pending, processing, completed, failed
        self.total = total_jobs
        self.completed = 0
        self.failed = 0
        self.current_job = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []

async def process_single_job(resume_text: str, job_url: str, use_rag: bool, batch_id: str, job_index: int) -> Dict[str, Any]:
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
                "tailored_resume": None
            }

        # Extract job title
        job_title = job_scraper.extract_job_title(job_url) or f"Job_{job_index + 1}"

        # Tailor resume using RAG or fallback
        if use_rag:
            langchain_processor.load_job_vectorstore()
            rag_result = langchain_processor.tailor_resume_with_rag(
                resume_text=resume_text,
                job_description=job_description,
                job_title=job_title
            )
            
            if rag_result:
                tailored_resume = rag_result.get("tailored_resume")
                similar_jobs_found = rag_result.get("similar_jobs_found", 0)
            else:
                # Fallback to standard processing
                tailored_resume = fallback_processor.tailor_resume(
                    resume_text, job_description, job_title
                )
                similar_jobs_found = 0
        else:
            tailored_resume = fallback_processor.tailor_resume(
                resume_text, job_description, job_title
            )
            similar_jobs_found = 0

        if not tailored_resume:
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": job_title,
                "status": "failed",
                "error": "Failed to generate tailored resume",
                "tailored_resume": None
            }

        # Perform diff analysis
        diff_analysis = diff_analyzer.analyze_resume_diff(
            original_text=resume_text,
            tailored_text=tailored_resume,
            job_title=job_title
        )

        # Store job description for future RAG
        if job_description and job_url:
            job_data = [{
                "id": f"{batch_id}_{job_index}",
                "job_description": job_description,
                "job_title": job_title,
                "url": job_url
            }]
            langchain_processor.initialize_job_vectorstore(job_data)

        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": job_title,
            "job_description": job_description,
            "status": "success",
            "tailored_resume": tailored_resume,
            "similar_jobs_found": similar_jobs_found,
            "enhancement_score": diff_analysis.get("enhancement_score", {}).get("overall_score"),
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
            "tailored_resume": None
        }

async def process_batch_jobs(batch_id: str, resume_text: str, job_urls: List[str], use_rag: bool, output_format: str):
    """Background task to process all jobs in a batch"""
    try:
        batch_jobs[batch_id].state = "processing"
        batch_jobs[batch_id].updated_at = datetime.now()
        
        results = []
        
        # Process jobs sequentially (could be made parallel for better performance)
        for i, job_url in enumerate(job_urls):
            result = await process_single_job(resume_text, job_url, use_rag, batch_id, i)
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
async def start_batch_processing(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """Start batch processing of multiple job URLs"""
    try:
        # Validate input
        if len(request.job_urls) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 job URLs allowed")
        
        if len(request.job_urls) == 0:
            raise HTTPException(status_code=400, detail="At least one job URL is required")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Initialize batch status
        batch_status = BatchJobStatus(batch_id, len(request.job_urls))
        batch_jobs[batch_id] = batch_status
        
        # Start background processing
        background_tasks.add_task(
            process_batch_jobs,
            batch_id,
            request.resume_text,
            request.job_urls,
            request.use_rag,
            request.output_format
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
        # Generate PDF
        pdf_buffer = generate_pdf_from_text(request.resume_text, request.job_title)
        
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

@router.post("/generate-zip")
async def generate_zip_file(request: ZIPGenerateRequest):
    """Generate a ZIP file containing multiple resume PDFs"""
    try:
        # Create temporary directory for ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
            zip_path = tmp_zip.name
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, resume_data in enumerate(request.resumes):
                try:
                    # Generate PDF for this resume
                    pdf_buffer = generate_pdf_from_text(
                        resume_data['resume_text'], 
                        resume_data['job_title']
                    )
                    
                    # Clean filename
                    safe_title = "".join(c for c in resume_data['job_title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title.replace(' ', '_')
                    filename = f"{i+1:02d}_{safe_title}.pdf"
                    
                    # Add PDF to ZIP
                    zipf.writestr(filename, pdf_buffer.getvalue())
                    
                    # Add a summary file for this resume
                    summary = f"""
Resume: {resume_data['job_title']}
Job URL: {resume_data['job_url']}
Enhancement Score: {resume_data.get('enhancement_score', 'N/A')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    zipf.writestr(f"{i+1:02d}_{safe_title}_info.txt", summary)
                    
                except Exception as e:
                    print(f"Error processing resume {i+1}: {str(e)}")
                    continue
            
            # Add batch summary
            batch_summary = f"""
BATCH PROCESSING SUMMARY
========================
Batch ID: {request.batch_id}
Total Resumes: {len(request.resumes)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This ZIP file contains:
- Individual PDF resumes for each job application
- Info files with job details and enhancement scores
- This summary file

All resumes have been tailored using AI for specific job requirements.
"""
            zipf.writestr("BATCH_SUMMARY.txt", batch_summary)
        
        # Return ZIP file
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"batch_resumes_{request.batch_id[:8]}.zip",
            background=BackgroundTasks(lambda: os.unlink(zip_path))  # Clean up after download
        )
        
    except Exception as e:
        # Clean up on error
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.unlink(zip_path)
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
        results = batch_results.get(batch_id, batch_status.results)
        
        return JSONResponse({
            "success": True,
            "batch_id": batch_id,
            "total_jobs": batch_status.total,
            "successful_jobs": len([r for r in results if r["status"] == "success"]),
            "failed_jobs": len([r for r in results if r["status"] == "failed"]),
            "results": results
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